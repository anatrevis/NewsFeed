import pytest
from fastapi import status


def test_keywords_endpoint_requires_auth(client):
    """Test that keywords endpoint returns 401 without authentication."""
    response = client.get("/api/keywords")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_articles_endpoint_requires_auth(client):
    """Test that articles endpoint returns 401 without authentication."""
    response = client.get("/api/articles")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_health_endpoint_is_public(client):
    """Test that health endpoint is accessible without auth."""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "healthy", "service": "newsfeed-api"}


def test_root_endpoint_is_public(client):
    """Test that root endpoint is accessible without auth."""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data
    assert data["message"] == "Welcome to NewsFeed API"


def test_authenticated_user_can_access_keywords(client, auth_headers, db_session):
    """Test that authenticated user can access keywords endpoint."""
    response = client.get("/api/keywords", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "keywords" in data
    assert "total" in data
    assert data["total"] == 0

