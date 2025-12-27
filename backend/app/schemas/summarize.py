"""Schemas for AI article summarization."""

from pydantic import BaseModel, Field


class ArticleForSummary(BaseModel):
    """Article data for summarization."""
    title: str
    description: str | None = None
    source: str | None = None


class SummarizeRequest(BaseModel):
    """Request schema for article summarization."""
    articles: list[ArticleForSummary] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="List of articles to summarize (1-50 articles)"
    )


class SummarizeResponse(BaseModel):
    """Response schema for article summarization."""
    summary: str = Field(..., description="AI-generated summary of the articles")


class SummarizeStatus(BaseModel):
    """Status of the summarization feature."""
    enabled: bool = Field(..., description="Whether OpenAI summarization is available")
    message: str | None = Field(
        None,
        description="Message explaining why the feature is disabled (if applicable)"
    )

