from enum import Enum
from pydantic import BaseModel
from datetime import datetime


class SortBy(str, Enum):
    """Valid sort options for News API."""
    relevancy = "relevancy"
    popularity = "popularity"
    published_at = "publishedAt"


class ArticleSource(BaseModel):
    """Schema for article source."""
    id: str | None = None
    name: str | None = None


class Article(BaseModel):
    """Schema for a news article from News API."""
    source: ArticleSource
    author: str | None = None
    title: str
    description: str | None = None
    url: str
    urlToImage: str | None = None
    publishedAt: datetime | None = None
    content: str | None = None


class ArticleList(BaseModel):
    """Schema for list of articles."""
    articles: list[Article]
    totalResults: int
    status: str = "ok"

