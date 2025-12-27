import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from app.services.news_service import NewsService


@pytest.fixture
def news_service():
    """Create a NewsService instance with a mock API key."""
    with patch('app.services.news_service.settings') as mock_settings:
        mock_settings.news_api_key = "test-api-key"
        mock_settings.news_api_base_url = "https://newsapi.org/v2"
        yield NewsService()


@pytest.mark.asyncio
async def test_fetch_articles_with_empty_keywords(news_service):
    """Test that empty keywords returns empty list."""
    result = await news_service.fetch_articles([])
    assert result.articles == []
    assert result.totalResults == 0


@pytest.mark.asyncio
async def test_fetch_articles_combines_keywords_with_or():
    """Test that keywords are combined with OR operator."""
    with patch('app.services.news_service.settings') as mock_settings:
        mock_settings.news_api_key = "test-api-key"
        mock_settings.news_api_base_url = "https://newsapi.org/v2"
        
        service = NewsService()
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ok",
            "totalResults": 0,
            "articles": []
        }
        
        with patch.object(httpx.AsyncClient, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            
            await service.fetch_articles(["python", "javascript", "react"])
            
            # Check that the query parameter includes OR
            call_kwargs = mock_get.call_args
            params = call_kwargs.kwargs.get('params', {})
            assert "OR" in params.get("q", "")


@pytest.mark.asyncio
async def test_fetch_articles_parses_response_correctly():
    """Test that API response is parsed into Article objects."""
    with patch('app.services.news_service.settings') as mock_settings:
        mock_settings.news_api_key = "test-api-key"
        mock_settings.news_api_base_url = "https://newsapi.org/v2"
        
        service = NewsService()
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ok",
            "totalResults": 1,
            "articles": [
                {
                    "source": {"id": "bbc", "name": "BBC News"},
                    "author": "John Doe",
                    "title": "Test Article",
                    "description": "Test description",
                    "url": "https://example.com/article",
                    "urlToImage": "https://example.com/image.jpg",
                    "publishedAt": "2024-01-15T10:00:00Z",
                    "content": "Full article content here"
                }
            ]
        }
        
        with patch.object(httpx.AsyncClient, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            
            result = await service.fetch_articles(["test"])
            
            assert result.totalResults == 1
            assert len(result.articles) == 1
            
            article = result.articles[0]
            assert article.title == "Test Article"
            assert article.author == "John Doe"
            assert article.source.name == "BBC News"
            assert article.url == "https://example.com/article"


@pytest.mark.asyncio
async def test_fetch_articles_raises_on_missing_api_key():
    """Test that missing API key raises ValueError."""
    with patch('app.services.news_service.settings') as mock_settings:
        mock_settings.news_api_key = ""
        mock_settings.news_api_base_url = "https://newsapi.org/v2"
        
        service = NewsService()
        
        with pytest.raises(ValueError, match="NEWS_API_KEY is not configured"):
            await service.fetch_articles(["test"])


@pytest.mark.asyncio
async def test_fetch_articles_handles_api_error():
    """Test that API errors are properly handled."""
    with patch('app.services.news_service.settings') as mock_settings:
        mock_settings.news_api_key = "test-api-key"
        mock_settings.news_api_base_url = "https://newsapi.org/v2"
        
        service = NewsService()
        
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "status": "error",
            "message": "Invalid API key"
        }
        
        with patch.object(httpx.AsyncClient, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            
            with pytest.raises(Exception, match="News API error"):
                await service.fetch_articles(["test"])


@pytest.mark.asyncio
async def test_fetch_articles_handles_timeout():
    """Test that timeouts are handled gracefully."""
    with patch('app.services.news_service.settings') as mock_settings:
        mock_settings.news_api_key = "test-api-key"
        mock_settings.news_api_base_url = "https://newsapi.org/v2"
        
        service = NewsService()
        
        with patch.object(httpx.AsyncClient, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = httpx.TimeoutException("Connection timed out")
            
            with pytest.raises(Exception, match="timed out"):
                await service.fetch_articles(["test"])


@pytest.mark.asyncio
async def test_fetch_articles_respects_pagination():
    """Test that pagination parameters are passed correctly."""
    with patch('app.services.news_service.settings') as mock_settings:
        mock_settings.news_api_key = "test-api-key"
        mock_settings.news_api_base_url = "https://newsapi.org/v2"
        
        service = NewsService()
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ok",
            "totalResults": 0,
            "articles": []
        }
        
        with patch.object(httpx.AsyncClient, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            
            await service.fetch_articles(["test"], page=3, page_size=50)
            
            call_kwargs = mock_get.call_args
            params = call_kwargs.kwargs.get('params', {})
            assert params.get("page") == 3
            assert params.get("pageSize") == 50

