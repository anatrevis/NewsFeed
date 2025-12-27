from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID


class KeywordCreate(BaseModel):
    """Schema for creating a keyword."""
    keyword: str = Field(..., min_length=1, max_length=100)


class KeywordResponse(BaseModel):
    """Schema for keyword response."""
    id: UUID
    keyword: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class KeywordList(BaseModel):
    """Schema for list of keywords."""
    keywords: list[KeywordResponse]
    total: int


class DeleteResponse(BaseModel):
    """Schema for delete operation response."""
    message: str

