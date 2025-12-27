"""Router for AI article summarization using OpenAI Responses API."""

from fastapi import APIRouter, HTTPException, status, Depends
from openai import OpenAI, AuthenticationError, RateLimitError, APIError, APITimeoutError

from app.config import get_settings
from app.schemas.summarize import SummarizeRequest, SummarizeResponse, SummarizeStatus
from app.services.auth_service import get_current_user
from app.logging_config import get_logger

router = APIRouter()
settings = get_settings()
logger = get_logger(__name__)


@router.get("/status", response_model=SummarizeStatus)
async def get_summarize_status():
    """
    Check if AI summarization is available.
    Returns enabled=true if OPENAI_API_KEY is configured.
    """
    if settings.openai_api_key:
        logger.debug("Summarization feature is enabled")
        return SummarizeStatus(enabled=True, message=None)
    
    logger.debug("Summarization feature is disabled - no API key")
    return SummarizeStatus(
        enabled=False,
        message="AI summarization requires an OpenAI API key. Add OPENAI_API_KEY to your .env file."
    )


@router.post("", response_model=SummarizeResponse)
async def summarize_articles(
    request: SummarizeRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Summarize a list of articles using OpenAI's Responses API.
    Requires authentication and OPENAI_API_KEY to be configured.
    """
    user_id = current_user.get("sub")
    
    # Check if OpenAI is configured
    if not settings.openai_api_key:
        logger.warning(f"Summarization attempted without API key | user={user_id}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI summarization requires an OpenAI API key. Add OPENAI_API_KEY to your .env file.",
        )
    
    # Build the prompt from articles
    articles_text = "\n\n".join([
        f"**{art.title}**\n"
        f"Source: {art.source or 'Unknown'}\n"
        f"Description: {art.description or 'No description'}"
        for art in request.articles
    ])
    
    prompt = f"""You are a news analyst. Summarize the following {len(request.articles)} news articles into a concise, informative summary. 
Highlight the main themes, key events, and important takeaways. Keep the summary to 2-3 paragraphs.

Articles:
{articles_text}

Summary:"""

    logger.info(f"Summarizing {len(request.articles)} articles | user={user_id}")
    logger.debug(f"Prompt length: {len(prompt)} characters")
    
    try:
        client = OpenAI(
            api_key=settings.openai_api_key,
            timeout=30.0,  # 30 second timeout
        )
        
        # Use the Responses API
        response = client.responses.create(
            model="gpt-4o-mini",
            input=prompt,
        )
        
        # Extract the summary from the response
        summary = response.output_text
        
        logger.info(f"Summary generated successfully | user={user_id} | length={len(summary)}")
        
        return SummarizeResponse(summary=summary)
        
    except APITimeoutError as e:
        logger.error(f"OpenAI request timed out | user={user_id} | error={str(e)}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="AI summarization request timed out. Please try again.",
        )
    except AuthenticationError as e:
        logger.error(f"OpenAI authentication failed | user={user_id} | error={str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid OpenAI API key. Please check your configuration.",
        )
    except RateLimitError as e:
        logger.warning(f"OpenAI rate limit exceeded | user={user_id} | error={str(e)}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="OpenAI rate limit exceeded. Please try again later.",
        )
    except APIError as e:
        logger.error(f"OpenAI API error | user={user_id} | error={str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"OpenAI service error: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Unexpected error during summarization | user={user_id} | error={str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to connect to AI service. Please try again.",
        )

