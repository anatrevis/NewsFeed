import httpx
from datetime import datetime, timedelta
from typing import Optional

from app.config import get_settings
from app.schemas.article import Article, ArticleList, ArticleSource
from app.logging_config import get_logger

settings = get_settings()
logger = get_logger(__name__)


class NewsService:
    """Service for fetching news from News API."""

    def __init__(self):
        self.api_key = settings.news_api_key
        self.base_url = settings.news_api_base_url

    async def fetch_articles(
        self,
        keywords: list[str],
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "publishedAt",
        language: str = "en",
        match_mode: str = "any",
    ) -> ArticleList:
        """
        Fetch articles from News API based on keywords.
        
        Args:
            keywords: List of keywords to search for
            page: Page number for pagination
            page_size: Number of articles per page (max 100)
            sort_by: Sort order (relevancy, popularity, publishedAt)
            language: Language code (en, es, fr, de, etc.)
            match_mode: 'any' (OR - match any keyword) or 'all' (AND - match all keywords)
        
        Returns:
            ArticleList with articles and total count
        """
        if not keywords:
            logger.debug("No keywords provided, returning empty list")
            return ArticleList(articles=[], totalResults=0)
        
        if not self.api_key:
            logger.error("NEWS_API_KEY is not configured")
            raise ValueError("NEWS_API_KEY is not configured")
        
        # Build query based on match mode
        if match_mode == "all":
            # AND - articles must contain all keywords (stricter)
            query = " AND ".join(keywords)
        else:
            # OR - articles can contain any keyword (broader, default)
            query = " OR ".join(keywords)
        
        # Search articles from the last 30 days (News API free tier limitation)
        from_date = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        params = {
            "q": query,
            "from": from_date,
            "sortBy": sort_by,
            "page": page,
            "pageSize": min(page_size, 100),
            "apiKey": self.api_key,
            "language": language,
        }
        
        logger.debug(
            f"News API request | query={query} | sort={sort_by} | "
            f"lang={language} | page={page} | mode={match_mode}"
        )
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/everything",
                    params=params,
                    timeout=15.0,
                )
                
                if response.status_code != 200:
                    error_data = response.json()
                    error_msg = error_data.get('message', 'Unknown error')
                    logger.error(f"News API error | status={response.status_code} | error={error_msg}")
                    raise Exception(f"News API error: {error_msg}")
                
                data = response.json()
                
                # Filter out articles with missing required fields (title, url)
                articles = []
                skipped = 0
                for art in data.get("articles", []):
                    title = art.get("title")
                    url = art.get("url")
                    # Skip articles without title or url
                    if not title or not url:
                        skipped += 1
                        continue
                    articles.append(Article(
                        source=ArticleSource(
                            id=art.get("source", {}).get("id"),
                            name=art.get("source", {}).get("name"),
                        ),
                        author=art.get("author"),
                        title=title,
                        description=art.get("description"),
                        url=url,
                        urlToImage=art.get("urlToImage"),
                        publishedAt=art.get("publishedAt"),
                        content=art.get("content"),
                    ))
                
                total_results = data.get("totalResults", 0)
                
                if skipped > 0:
                    logger.debug(f"Skipped {skipped} articles with missing title/url")
                
                logger.info(
                    f"News API response | articles={len(articles)} | "
                    f"total={total_results} | query={query[:50]}..."
                )
                
                return ArticleList(
                    articles=articles,
                    totalResults=total_results,
                    status=data.get("status", "ok"),
                )
                
        except httpx.TimeoutException:
            logger.error(f"News API timeout | query={query[:50]}...")
            raise Exception("News API request timed out")
        except httpx.RequestError as e:
            logger.error(f"News API connection error | error={str(e)}")
            raise Exception(f"Failed to connect to News API: {str(e)}")

    async def get_article_by_url(self, url: str) -> Optional[Article]:
        """
        Get a single article by URL.
        Note: News API doesn't have a direct endpoint for this,
        so we return minimal info that the frontend can use.
        """
        # For detail view, frontend can use the URL directly
        # This is a placeholder if we need to fetch more data
        return None
