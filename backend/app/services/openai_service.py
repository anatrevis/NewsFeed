"""Service for AI-powered article summarization using OpenAI."""

from typing import List
from openai import OpenAI, AuthenticationError, RateLimitError, APIError, APITimeoutError

from app.config import get_settings
from app.logging_config import get_logger

settings = get_settings()
logger = get_logger(__name__)


class OpenAIServiceError(Exception):
    """Base exception for OpenAI service errors."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class OpenAITimeoutError(OpenAIServiceError):
    """Request to OpenAI timed out."""
    def __init__(self, message: str = "AI summarization request timed out. Please try again."):
        super().__init__(message, status_code=504)


class OpenAIAuthError(OpenAIServiceError):
    """Invalid OpenAI API key."""
    def __init__(self, message: str = "Invalid OpenAI API key. Please check your configuration."):
        super().__init__(message, status_code=401)


class OpenAIRateLimitError(OpenAIServiceError):
    """OpenAI rate limit exceeded."""
    def __init__(self, message: str = "OpenAI rate limit exceeded. Please try again later."):
        super().__init__(message, status_code=429)


class OpenAIAPIError(OpenAIServiceError):
    """OpenAI API error."""
    def __init__(self, message: str = "OpenAI service error"):
        super().__init__(message, status_code=502)


class OpenAIService:
    """Service for interacting with OpenAI API."""

    TIMEOUT_SECONDS = 30.0
    MODEL = "gpt-4o-mini"

    def __init__(self):
        self.api_key = settings.openai_api_key
        self._client = None

    @property
    def is_enabled(self) -> bool:
        """Check if OpenAI is configured."""
        return bool(self.api_key)

    @property
    def client(self) -> OpenAI:
        """Lazy initialization of OpenAI client."""
        if self._client is None:
            if not self.api_key:
                raise OpenAIServiceError(
                    "AI summarization requires an OpenAI API key. Add OPENAI_API_KEY to your .env file.",
                    status_code=503
                )
            self._client = OpenAI(
                api_key=self.api_key,
                timeout=self.TIMEOUT_SECONDS,
            )
        return self._client

    def _build_prompt(self, articles: List[dict]) -> str:
        """Build the summarization prompt from articles."""
        articles_text = "\n\n".join([
            f"**{art.get('title', 'Untitled')}**\n"
            f"Source: {art.get('source', 'Unknown')}\n"
            f"Description: {art.get('description', 'No description')}"
            for art in articles
        ])

        return f"""You are a news analyst. Summarize the following {len(articles)} news articles into a concise, informative summary. 
Highlight the main themes, key events, and important takeaways. Keep the summary to 2-3 paragraphs.

Articles:
{articles_text}

Summary:"""

    async def summarize_articles(self, articles: List[dict]) -> str:
        """
        Summarize a list of articles using OpenAI's Responses API.
        
        Args:
            articles: List of article dicts with 'title', 'source', 'description' keys
            
        Returns:
            Summary string
            
        Raises:
            OpenAIServiceError: On any OpenAI-related error
        """
        if not articles:
            return "No articles to summarize."

        prompt = self._build_prompt(articles)
        
        logger.debug(f"OpenAI prompt length: {len(prompt)} characters")

        try:
            response = self.client.responses.create(
                model=self.MODEL,
                input=prompt,
            )
            
            summary = response.output_text
            logger.debug(f"OpenAI response length: {len(summary)} characters")
            
            return summary

        except APITimeoutError as e:
            logger.error(f"OpenAI timeout | error={str(e)}")
            raise OpenAITimeoutError()
        except AuthenticationError as e:
            logger.error(f"OpenAI auth error | error={str(e)}")
            raise OpenAIAuthError()
        except RateLimitError as e:
            logger.warning(f"OpenAI rate limit | error={str(e)}")
            raise OpenAIRateLimitError()
        except APIError as e:
            logger.error(f"OpenAI API error | error={str(e)}")
            raise OpenAIAPIError(f"OpenAI service error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected OpenAI error | error={str(e)}", exc_info=True)
            raise OpenAIServiceError("Unable to connect to AI service. Please try again.")

