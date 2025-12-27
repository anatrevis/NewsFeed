from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.keyword import UserKeyword
from app.schemas.keyword import KeywordCreate, KeywordResponse, KeywordList, DeleteResponse
from app.services.auth_service import get_current_user
from app.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("", response_model=KeywordList)
async def get_keywords(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get all keywords for the current user."""
    user_id = current_user.get("sub")
    
    keywords = (
        db.query(UserKeyword)
        .filter(UserKeyword.user_id == user_id)
        .order_by(UserKeyword.created_at.desc())
        .all()
    )
    
    logger.debug(f"Retrieved {len(keywords)} keywords for user {user_id}")
    
    return KeywordList(
        keywords=[KeywordResponse.model_validate(kw) for kw in keywords],
        total=len(keywords),
    )


@router.post("", response_model=KeywordResponse, status_code=status.HTTP_201_CREATED)
async def create_keyword(
    keyword_data: KeywordCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Add a new keyword for the current user."""
    user_id = current_user.get("sub")
    
    # Normalize keyword (lowercase, trimmed)
    normalized_keyword = keyword_data.keyword.strip().lower()
    
    keyword = UserKeyword(
        user_id=user_id,
        keyword=normalized_keyword,
    )
    
    try:
        db.add(keyword)
        db.commit()
        db.refresh(keyword)
        logger.info(f"Keyword created | user={user_id} | keyword={normalized_keyword}")
    except IntegrityError:
        db.rollback()
        logger.warning(f"Duplicate keyword attempt | user={user_id} | keyword={normalized_keyword}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Keyword '{normalized_keyword}' already exists",
        )
    
    return keyword


@router.delete("/{keyword}", response_model=DeleteResponse)
async def delete_keyword(
    keyword: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Remove a keyword for the current user."""
    user_id = current_user.get("sub")
    
    # Normalize keyword for lookup
    normalized_keyword = keyword.strip().lower()
    
    db_keyword = (
        db.query(UserKeyword)
        .filter(
            UserKeyword.user_id == user_id,
            UserKeyword.keyword == normalized_keyword,
        )
        .first()
    )
    
    if not db_keyword:
        logger.warning(f"Keyword not found for deletion | user={user_id} | keyword={normalized_keyword}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Keyword '{keyword}' not found",
        )
    
    db.delete(db_keyword)
    db.commit()
    
    logger.info(f"Keyword deleted | user={user_id} | keyword={normalized_keyword}")
    
    return DeleteResponse(message=f"Keyword '{keyword}' deleted successfully")
