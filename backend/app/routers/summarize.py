"""Router for AI article summarization."""

from fastapi import APIRouter, HTTPException, Depends

from app.schemas.summarize import SummarizeRequest, SummarizeResponse, SummarizeStatus
from app.services.auth_service import get_current_user
from app.services.openai_service import OpenAIService, OpenAIServiceError
from app.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)

# Service instance (could be injected via dependency in production)
openai_service = OpenAIService()


@router.get("/status", response_model=SummarizeStatus)
async def get_summarize_status():
    """
    Check if AI summarization is available.
    Returns enabled=true if OPENAI_API_KEY is configured.
    """
    if openai_service.is_enabled:
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
    
    logger.info(f"Summarizing {len(request.articles)} articles | user={user_id}")
    
    # Convert request articles to dict format expected by service
    articles_data = [
        {
            "title": art.title,
            "source": art.source,
            "description": art.description,
        }
        for art in request.articles
    ]
    
    try:
        summary = await openai_service.summarize_articles(articles_data)
        
        logger.info(f"Summary generated | user={user_id} | length={len(summary)}")
        
        return SummarizeResponse(summary=summary)
        
    except OpenAIServiceError as e:
        logger.error(f"OpenAI service error | user={user_id} | error={e.message}")
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message,
        )
