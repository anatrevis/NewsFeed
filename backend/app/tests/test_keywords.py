import pytest
from fastapi import status


def test_create_keyword(client, auth_headers, db_session):
    """Test creating a new keyword."""
    response = client.post(
        "/api/keywords",
        json={"keyword": "Python"},
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["keyword"] == "python"  # Should be normalized to lowercase
    assert "id" in data
    assert "created_at" in data


def test_create_keyword_normalizes_to_lowercase(client, auth_headers, db_session):
    """Test that keywords are normalized to lowercase."""
    response = client.post(
        "/api/keywords",
        json={"keyword": "JAVASCRIPT"},
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["keyword"] == "javascript"


def test_create_keyword_trims_whitespace(client, auth_headers, db_session):
    """Test that keywords have whitespace trimmed."""
    response = client.post(
        "/api/keywords",
        json={"keyword": "  react  "},
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["keyword"] == "react"


def test_create_duplicate_keyword_returns_409(client, auth_headers, db_session):
    """Test that creating a duplicate keyword returns 409 Conflict."""
    # Create first keyword
    client.post(
        "/api/keywords",
        json={"keyword": "docker"},
        headers=auth_headers,
    )
    
    # Try to create duplicate
    response = client.post(
        "/api/keywords",
        json={"keyword": "docker"},
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_409_CONFLICT


def test_get_keywords(client, auth_headers, db_session):
    """Test retrieving all keywords for a user."""
    # Create some keywords
    client.post("/api/keywords", json={"keyword": "python"}, headers=auth_headers)
    client.post("/api/keywords", json={"keyword": "fastapi"}, headers=auth_headers)
    client.post("/api/keywords", json={"keyword": "react"}, headers=auth_headers)
    
    # Get keywords
    response = client.get("/api/keywords", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 3
    assert len(data["keywords"]) == 3
    
    # Check keywords are present (order may vary)
    keyword_values = [k["keyword"] for k in data["keywords"]]
    assert "python" in keyword_values
    assert "fastapi" in keyword_values
    assert "react" in keyword_values


def test_delete_keyword(client, auth_headers, db_session):
    """Test deleting a keyword."""
    # Create keyword
    client.post("/api/keywords", json={"keyword": "kubernetes"}, headers=auth_headers)
    
    # Verify it exists
    response = client.get("/api/keywords", headers=auth_headers)
    assert response.json()["total"] == 1
    
    # Delete keyword
    response = client.delete("/api/keywords/kubernetes", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    
    # Verify it's gone
    response = client.get("/api/keywords", headers=auth_headers)
    assert response.json()["total"] == 0


def test_delete_nonexistent_keyword_returns_404(client, auth_headers, db_session):
    """Test that deleting a non-existent keyword returns 404."""
    response = client.delete("/api/keywords/nonexistent", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_empty_keyword_rejected(client, auth_headers, db_session):
    """Test that empty keyword is rejected."""
    response = client.post(
        "/api/keywords",
        json={"keyword": ""},
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_keywords_are_user_specific(client, auth_headers, db_session, mocker):
    """Test that keywords are isolated per user."""
    from app.services.auth_service import get_current_user
    
    # Create keyword as first user
    client.post("/api/keywords", json={"keyword": "user1keyword"}, headers=auth_headers)
    
    # Switch to second user
    async def mock_user2():
        return {"sub": "user-2", "email": "user2@example.com"}
    
    app = client.app
    app.dependency_overrides[get_current_user] = mock_user2
    
    # Second user should not see first user's keywords
    response = client.get("/api/keywords", headers=auth_headers)
    assert response.json()["total"] == 0
    
    # Second user can create their own keyword
    client.post("/api/keywords", json={"keyword": "user2keyword"}, headers=auth_headers)
    response = client.get("/api/keywords", headers=auth_headers)
    assert response.json()["total"] == 1
    assert response.json()["keywords"][0]["keyword"] == "user2keyword"

