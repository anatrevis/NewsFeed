from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.keyword import UserKeyword
from app.schemas.article import ArticleList, SortBy, Language, MatchMode
from app.services.auth_service import get_current_user
from app.services.news_service import NewsService
from app.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("", response_model=ArticleList)
async def get_articles(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Articles per page"),
    sort_by: SortBy = Query(SortBy.published_at, description="Sort by: relevancy, popularity, publishedAt"),
    language: Language = Query(Language.en, description="Article language"),
    match_mode: MatchMode = Query(MatchMode.any, description="Keyword matching: 'any' (OR) or 'all' (AND)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get articles based on the current user's saved keywords.
    
    - match_mode='any': Returns articles matching ANY of the user's keywords (OR logic)
    - match_mode='all': Returns articles matching ALL of the user's keywords (AND logic)
    
    If the user has no keywords, returns an empty list.
    """
    user_id = current_user.get("sub")
    
    # Get user's keywords
    user_keywords = (
        db.query(UserKeyword)
        .filter(UserKeyword.user_id == user_id)
        .all()
    )
    
    keywords = [kw.keyword for kw in user_keywords]
    
    if not keywords:
        logger.debug(f"No keywords found for user {user_id}, returning empty list")
        return ArticleList(articles=[], totalResults=0)
    
    # Fetch articles from News API
    news_service = NewsService()
    
    logger.debug(
        f"Fetching articles | user={user_id} | keywords={keywords} | "
        f"page={page} | sort={sort_by.value} | lang={language.value} | mode={match_mode.value}"
    )
    
    try:
        articles = await news_service.fetch_articles(
            keywords=keywords,
            page=page,
            page_size=page_size,
            sort_by=sort_by.value,
            language=language.value,
            match_mode=match_mode.value,
        )
        
        logger.info(
            f"Articles fetched | user={user_id} | count={len(articles.articles)} | "
            f"total={articles.totalResults}"
        )
        
        return articles
    except ValueError as e:
        logger.error(f"Configuration error fetching articles | user={user_id} | error={str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to fetch articles | user={user_id} | error={str(e)}", exc_info=True)
        raise HTTPException(status_code=502, detail=f"Failed to fetch articles: {str(e)}")
