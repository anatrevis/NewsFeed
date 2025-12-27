import pytest
from fastapi import status
from unittest.mock import AsyncMock, patch, MagicMock

from app.schemas.article import ArticleList, Article, ArticleSource, SortBy


@pytest.fixture
def mock_articles_response():
    """Create a mock articles response."""
    return ArticleList(
        articles=[
            Article(
                source=ArticleSource(id="bbc", name="BBC News"),
                author="John Doe",
                title="Test Article 1",
                description="Test description 1",
                url="https://example.com/article1",
                urlToImage="https://example.com/image1.jpg",
                publishedAt="2024-01-15T10:00:00Z",
                content="Full article content here",
            ),
            Article(
                source=ArticleSource(id="cnn", name="CNN"),
                author="Jane Smith",
                title="Test Article 2",
                description="Test description 2",
                url="https://example.com/article2",
                urlToImage="https://example.com/image2.jpg",
                publishedAt="2024-01-14T10:00:00Z",
                content="Another article content",
            ),
        ],
        totalResults=2,
        status="ok",
    )


def test_get_articles_requires_auth(client):
    """Test that articles endpoint returns 401 without authentication."""
    response = client.get("/api/articles")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_articles_with_no_keywords(client, auth_headers, db_session):
    """Test that articles returns empty list when user has no keywords."""
    response = client.get("/api/articles", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["articles"] == []
    assert data["totalResults"] == 0


def test_get_articles_with_keywords(client, auth_headers, db_session, mock_articles_response):
    """Test fetching articles when user has keywords."""
    # Add a keyword first
    client.post("/api/keywords", json={"keyword": "python"}, headers=auth_headers)
    
    with patch("app.routers.articles.NewsService") as MockNewsService:
        mock_service = MagicMock()
        mock_service.fetch_articles = AsyncMock(return_value=mock_articles_response)
        MockNewsService.return_value = mock_service
        
        response = client.get("/api/articles", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["articles"]) == 2
        assert data["totalResults"] == 2
        assert data["articles"][0]["title"] == "Test Article 1"
        
        # Verify the service was called with correct arguments
        mock_service.fetch_articles.assert_called_once()
        call_kwargs = mock_service.fetch_articles.call_args.kwargs
        assert "python" in call_kwargs["keywords"]


def test_get_articles_pagination(client, auth_headers, db_session, mock_articles_response):
    """Test articles pagination parameters."""
    client.post("/api/keywords", json={"keyword": "tech"}, headers=auth_headers)
    
    with patch("app.routers.articles.NewsService") as MockNewsService:
        mock_service = MagicMock()
        mock_service.fetch_articles = AsyncMock(return_value=mock_articles_response)
        MockNewsService.return_value = mock_service
        
        response = client.get(
            "/api/articles?page=2&page_size=50",
            headers=auth_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        call_kwargs = mock_service.fetch_articles.call_args.kwargs
        assert call_kwargs["page"] == 2
        assert call_kwargs["page_size"] == 50


def test_get_articles_invalid_page_rejected(client, auth_headers, db_session):
    """Test that invalid page number is rejected."""
    response = client.get("/api/articles?page=0", headers=auth_headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_articles_invalid_page_size_rejected(client, auth_headers, db_session):
    """Test that page_size over 100 is rejected."""
    response = client.get("/api/articles?page_size=101", headers=auth_headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_articles_negative_page_size_rejected(client, auth_headers, db_session):
    """Test that negative page_size is rejected."""
    response = client.get("/api/articles?page_size=-1", headers=auth_headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_articles_sort_by_relevancy(client, auth_headers, db_session, mock_articles_response):
    """Test sorting by relevancy."""
    client.post("/api/keywords", json={"keyword": "news"}, headers=auth_headers)
    
    with patch("app.routers.articles.NewsService") as MockNewsService:
        mock_service = MagicMock()
        mock_service.fetch_articles = AsyncMock(return_value=mock_articles_response)
        MockNewsService.return_value = mock_service
        
        response = client.get(
            "/api/articles?sort_by=relevancy",
            headers=auth_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        call_kwargs = mock_service.fetch_articles.call_args.kwargs
        assert call_kwargs["sort_by"] == "relevancy"


def test_get_articles_sort_by_popularity(client, auth_headers, db_session, mock_articles_response):
    """Test sorting by popularity."""
    client.post("/api/keywords", json={"keyword": "news"}, headers=auth_headers)
    
    with patch("app.routers.articles.NewsService") as MockNewsService:
        mock_service = MagicMock()
        mock_service.fetch_articles = AsyncMock(return_value=mock_articles_response)
        MockNewsService.return_value = mock_service
        
        response = client.get(
            "/api/articles?sort_by=popularity",
            headers=auth_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        call_kwargs = mock_service.fetch_articles.call_args.kwargs
        assert call_kwargs["sort_by"] == "popularity"


def test_get_articles_sort_by_published_at(client, auth_headers, db_session, mock_articles_response):
    """Test sorting by publishedAt (default)."""
    client.post("/api/keywords", json={"keyword": "news"}, headers=auth_headers)
    
    with patch("app.routers.articles.NewsService") as MockNewsService:
        mock_service = MagicMock()
        mock_service.fetch_articles = AsyncMock(return_value=mock_articles_response)
        MockNewsService.return_value = mock_service
        
        response = client.get("/api/articles", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        call_kwargs = mock_service.fetch_articles.call_args.kwargs
        assert call_kwargs["sort_by"] == "publishedAt"


def test_get_articles_invalid_sort_by_rejected(client, auth_headers, db_session):
    """Test that invalid sort_by value is rejected."""
    response = client.get(
        "/api/articles?sort_by=invalid_sort",
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_articles_handles_service_value_error(client, auth_headers, db_session):
    """Test that ValueError from service returns 500."""
    client.post("/api/keywords", json={"keyword": "test"}, headers=auth_headers)
    
    with patch("app.routers.articles.NewsService") as MockNewsService:
        mock_service = MagicMock()
        mock_service.fetch_articles = AsyncMock(
            side_effect=ValueError("NEWS_API_KEY is not configured")
        )
        MockNewsService.return_value = mock_service
        
        response = client.get("/api/articles", headers=auth_headers)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "NEWS_API_KEY" in response.json()["detail"]


def test_get_articles_handles_service_exception(client, auth_headers, db_session):
    """Test that generic exceptions from service return 502."""
    client.post("/api/keywords", json={"keyword": "test"}, headers=auth_headers)
    
    with patch("app.routers.articles.NewsService") as MockNewsService:
        mock_service = MagicMock()
        mock_service.fetch_articles = AsyncMock(
            side_effect=Exception("News API error: Rate limit exceeded")
        )
        MockNewsService.return_value = mock_service
        
        response = client.get("/api/articles", headers=auth_headers)
        
        assert response.status_code == status.HTTP_502_BAD_GATEWAY
        assert "Failed to fetch articles" in response.json()["detail"]


def test_get_articles_multiple_keywords(client, auth_headers, db_session, mock_articles_response):
    """Test fetching articles with multiple keywords."""
    # Add multiple keywords
    client.post("/api/keywords", json={"keyword": "python"}, headers=auth_headers)
    client.post("/api/keywords", json={"keyword": "javascript"}, headers=auth_headers)
    client.post("/api/keywords", json={"keyword": "react"}, headers=auth_headers)
    
    with patch("app.routers.articles.NewsService") as MockNewsService:
        mock_service = MagicMock()
        mock_service.fetch_articles = AsyncMock(return_value=mock_articles_response)
        MockNewsService.return_value = mock_service
        
        response = client.get("/api/articles", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        call_kwargs = mock_service.fetch_articles.call_args.kwargs
        keywords = call_kwargs["keywords"]
        assert len(keywords) == 3
        assert "python" in keywords
        assert "javascript" in keywords
        assert "react" in keywords


class TestSortByEnum:
    """Tests for the SortBy enum."""
    
    def test_sort_by_values(self):
        """Test that SortBy enum has correct values."""
        assert SortBy.relevancy.value == "relevancy"
        assert SortBy.popularity.value == "popularity"
        assert SortBy.published_at.value == "publishedAt"
    
    def test_sort_by_is_string_enum(self):
        """Test that SortBy enum members are strings."""
        assert isinstance(SortBy.relevancy, str)
        assert isinstance(SortBy.popularity, str)
        assert isinstance(SortBy.published_at, str)

