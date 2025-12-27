import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
import jwt
from datetime import datetime, timedelta

from app.main import app
from app.schemas.auth import SignupRequest, LoginRequest
from app.services.auth_service import AuthService


# ============================================
# SCHEMA VALIDATION TESTS
# ============================================

class TestUsernameValidation:
    """Test username validation rules."""
    
    def test_valid_username_lowercase_letters(self):
        """Valid username with only lowercase letters."""
        request = SignupRequest(
            username="validuser",
            email="test@example.com",
            password="SecurePass123!"
        )
        assert request.username == "validuser"
    
    def test_valid_username_lowercase_with_numbers(self):
        """Valid username with lowercase letters and numbers."""
        request = SignupRequest(
            username="user123",
            email="test@example.com",
            password="SecurePass123!"
        )
        assert request.username == "user123"
    
    def test_valid_username_only_numbers(self):
        """Valid username with only numbers."""
        request = SignupRequest(
            username="123456",
            email="test@example.com",
            password="SecurePass123!"
        )
        assert request.username == "123456"
    
    def test_invalid_username_uppercase(self):
        """Username with uppercase letters should be rejected."""
        with pytest.raises(ValueError, match="lowercase letters and numbers"):
            SignupRequest(
                username="TestUser",
                email="test@example.com",
                password="SecurePass123!"
            )
    
    def test_invalid_username_spaces(self):
        """Username with spaces should be rejected."""
        with pytest.raises(ValueError, match="lowercase letters and numbers"):
            SignupRequest(
                username="test user",
                email="test@example.com",
                password="SecurePass123!"
            )
    
    def test_invalid_username_underscore(self):
        """Username with underscore should be rejected."""
        with pytest.raises(ValueError, match="lowercase letters and numbers"):
            SignupRequest(
                username="test_user",
                email="test@example.com",
                password="SecurePass123!"
            )
    
    def test_invalid_username_hyphen(self):
        """Username with hyphen should be rejected."""
        with pytest.raises(ValueError, match="lowercase letters and numbers"):
            SignupRequest(
                username="test-user",
                email="test@example.com",
                password="SecurePass123!"
            )
    
    def test_invalid_username_special_chars(self):
        """Username with special characters should be rejected."""
        with pytest.raises(ValueError, match="lowercase letters and numbers"):
            SignupRequest(
                username="user@123!",
                email="test@example.com",
                password="SecurePass123!"
            )
    
    def test_invalid_username_mixed_case(self):
        """Username with mixed case should be rejected."""
        with pytest.raises(ValueError, match="lowercase letters and numbers"):
            SignupRequest(
                username="UserName",
                email="test@example.com",
                password="SecurePass123!"
            )
    
    def test_username_minimum_length(self):
        """Username must be at least 3 characters."""
        with pytest.raises(ValueError):
            SignupRequest(
                username="ab",
                email="test@example.com",
                password="SecurePass123!"
            )
    
    def test_username_maximum_length(self):
        """Username must be at most 50 characters."""
        with pytest.raises(ValueError):
            SignupRequest(
                username="a" * 51,
                email="test@example.com",
                password="SecurePass123!"
            )


class TestPasswordValidation:
    """Test password validation rules."""
    
    def test_valid_password(self):
        """Valid password with 8+ characters."""
        request = SignupRequest(
            username="testuser",
            email="test@example.com",
            password="SecurePass123!"
        )
        assert request.password == "SecurePass123!"
    
    def test_password_minimum_length(self):
        """Password must be at least 8 characters."""
        with pytest.raises(ValueError):
            SignupRequest(
                username="testuser",
                email="test@example.com",
                password="short"
            )


class TestEmailValidation:
    """Test email validation."""
    
    def test_valid_email(self):
        """Valid email format."""
        request = SignupRequest(
            username="testuser",
            email="user@example.com",
            password="SecurePass123!"
        )
        assert request.email == "user@example.com"
    
    def test_invalid_email_no_at(self):
        """Email without @ should be rejected."""
        with pytest.raises(ValueError):
            SignupRequest(
                username="testuser",
                email="userexample.com",
                password="SecurePass123!"
            )
    
    def test_invalid_email_no_domain(self):
        """Email without domain should be rejected."""
        with pytest.raises(ValueError):
            SignupRequest(
                username="testuser",
                email="user@",
                password="SecurePass123!"
            )


# ============================================
# AUTH SERVICE TESTS
# ============================================

class TestAuthServiceJWTValidation:
    """Test JWT token validation in auth service."""
    
    def test_validate_valid_app_jwt(self):
        """Valid app JWT should be decoded correctly."""
        auth_service = AuthService()
        
        # Create a valid token
        payload = {
            "sub": "123",
            "email": "test@example.com",
            "name": "Test User",
            "preferred_username": "testuser",
            "exp": datetime.utcnow() + timedelta(hours=1),
            "iat": datetime.utcnow(),
        }
        token = jwt.encode(payload, auth_service.jwt_secret, algorithm="HS256")
        
        result = auth_service.validate_app_jwt(token)
        
        assert result is not None
        assert result["sub"] == "123"
        assert result["email"] == "test@example.com"
        assert result["preferred_username"] == "testuser"
    
    def test_validate_expired_jwt(self):
        """Expired JWT should return None."""
        auth_service = AuthService()
        
        # Create an expired token
        payload = {
            "sub": "123",
            "email": "test@example.com",
            "exp": datetime.utcnow() - timedelta(hours=1),  # Expired
            "iat": datetime.utcnow() - timedelta(hours=2),
        }
        token = jwt.encode(payload, auth_service.jwt_secret, algorithm="HS256")
        
        result = auth_service.validate_app_jwt(token)
        
        assert result is None
    
    def test_validate_invalid_signature(self):
        """JWT with wrong signature should return None."""
        auth_service = AuthService()
        
        # Create token with wrong secret
        payload = {
            "sub": "123",
            "email": "test@example.com",
            "exp": datetime.utcnow() + timedelta(hours=1),
        }
        token = jwt.encode(payload, "wrong-secret", algorithm="HS256")
        
        result = auth_service.validate_app_jwt(token)
        
        assert result is None
    
    def test_validate_malformed_jwt(self):
        """Malformed JWT should return None."""
        auth_service = AuthService()
        
        result = auth_service.validate_app_jwt("not-a-valid-jwt")
        
        assert result is None


# ============================================
# API ENDPOINT TESTS
# ============================================

class TestSignupEndpoint:
    """Test signup endpoint validation."""
    
    def test_signup_invalid_username_uppercase_returns_422(self, client):
        """Signup with uppercase username should return 422."""
        response = client.post(
            "/api/auth/signup",
            json={
                "username": "TestUser",
                "email": "test@example.com",
                "password": "SecurePass123!"
            }
        )
        assert response.status_code == 422
        assert "lowercase" in response.json()["detail"][0]["msg"].lower()
    
    def test_signup_invalid_username_spaces_returns_422(self, client):
        """Signup with spaces in username should return 422."""
        response = client.post(
            "/api/auth/signup",
            json={
                "username": "test user",
                "email": "test@example.com",
                "password": "SecurePass123!"
            }
        )
        assert response.status_code == 422
    
    def test_signup_invalid_username_special_chars_returns_422(self, client):
        """Signup with special chars in username should return 422."""
        response = client.post(
            "/api/auth/signup",
            json={
                "username": "test_user!",
                "email": "test@example.com",
                "password": "SecurePass123!"
            }
        )
        assert response.status_code == 422
    
    def test_signup_short_username_returns_422(self, client):
        """Signup with too short username should return 422."""
        response = client.post(
            "/api/auth/signup",
            json={
                "username": "ab",
                "email": "test@example.com",
                "password": "SecurePass123!"
            }
        )
        assert response.status_code == 422
    
    def test_signup_short_password_returns_422(self, client):
        """Signup with too short password should return 422."""
        response = client.post(
            "/api/auth/signup",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "short"
            }
        )
        assert response.status_code == 422
    
    def test_signup_invalid_email_returns_422(self, client):
        """Signup with invalid email should return 422."""
        response = client.post(
            "/api/auth/signup",
            json={
                "username": "testuser",
                "email": "not-an-email",
                "password": "SecurePass123!"
            }
        )
        assert response.status_code == 422


class TestLoginEndpoint:
    """Test login endpoint."""
    
    def test_login_empty_username_returns_422(self, client):
        """Login with empty username should return 422."""
        response = client.post(
            "/api/auth/login",
            json={
                "username": "",
                "password": "password123"
            }
        )
        assert response.status_code == 422
    
    def test_login_empty_password_returns_422(self, client):
        """Login with empty password should return 422."""
        response = client.post(
            "/api/auth/login",
            json={
                "username": "testuser",
                "password": ""
            }
        )
        assert response.status_code == 422


class TestLogoutEndpoint:
    """Test logout endpoint."""
    
    def test_logout_without_token_succeeds(self, client):
        """Logout without token should succeed."""
        response = client.post("/api/auth/logout")
        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"
    
    def test_logout_with_token_succeeds(self, client):
        """Logout with token should succeed."""
        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": "Bearer some-token"}
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"


# ============================================
# INTEGRATION TESTS (MOCKED)
# ============================================

class TestSignupWithMockedAuthentik:
    """Test signup flow with mocked Authentik responses."""
    
    @pytest.mark.asyncio
    async def test_signup_success(self, client):
        """Successful signup should return 201."""
        with patch("app.services.authentik_service.httpx.AsyncClient") as mock_client:
            # Mock the flow initialization
            mock_init_response = MagicMock()
            mock_init_response.status_code = 200
            mock_init_response.json.return_value = {
                "component": "ak-stage-prompt",
                "fields": []
            }
            
            # Mock the registration response (success)
            mock_register_response = MagicMock()
            mock_register_response.status_code = 200
            mock_register_response.json.return_value = {
                "type": "redirect",
                "component": "xak-flow-redirect",
                "to": "/"
            }
            
            mock_instance = AsyncMock()
            mock_instance.get.return_value = mock_init_response
            mock_instance.post.return_value = mock_register_response
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.__aexit__.return_value = None
            mock_client.return_value = mock_instance
            
            response = client.post(
                "/api/auth/signup",
                json={
                    "username": "newuser",
                    "email": "new@example.com",
                    "password": "SecurePass123!"
                }
            )
            
            assert response.status_code == 201
            assert response.json()["username"] == "newuser"
            assert "Account created successfully" in response.json()["message"]
    
    @pytest.mark.asyncio
    async def test_signup_duplicate_email(self, client):
        """Signup with duplicate email should return 409."""
        with patch("app.services.authentik_service.httpx.AsyncClient") as mock_client:
            mock_init_response = MagicMock()
            mock_init_response.status_code = 200
            mock_init_response.json.return_value = {
                "component": "ak-stage-prompt"
            }
            
            # Mock duplicate email error
            mock_register_response = MagicMock()
            mock_register_response.status_code = 200
            mock_register_response.json.return_value = {
                "component": "ak-stage-access-denied",
                "error_message": "Failed to update user. Email already exists."
            }
            
            mock_instance = AsyncMock()
            mock_instance.get.return_value = mock_init_response
            mock_instance.post.return_value = mock_register_response
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.__aexit__.return_value = None
            mock_client.return_value = mock_instance
            
            response = client.post(
                "/api/auth/signup",
                json={
                    "username": "newuser",
                    "email": "existing@example.com",
                    "password": "SecurePass123!"
                }
            )
            
            assert response.status_code == 409
            assert "already taken" in response.json()["detail"].lower()


class TestLoginWithMockedAuthentik:
    """Test login flow with mocked Authentik responses."""
    
    @pytest.mark.asyncio
    async def test_login_success(self, client):
        """Successful login should return token and user info."""
        with patch("app.services.authentik_service.httpx.AsyncClient") as mock_client:
            # Mock flow initialization
            mock_init_response = MagicMock()
            mock_init_response.status_code = 200
            mock_init_response.json.return_value = {
                "component": "ak-stage-identification"
            }
            
            # Mock successful login redirect
            mock_login_response = MagicMock()
            mock_login_response.status_code = 200
            mock_login_response.json.return_value = {
                "type": "redirect",
                "to": "/"
            }
            
            # Mock user info response
            mock_user_response = MagicMock()
            mock_user_response.status_code = 200
            mock_user_response.json.return_value = {
                "user": {
                    "pk": 123,
                    "email": "test@example.com",
                    "name": "Test User",
                    "username": "testuser"
                }
            }
            
            mock_instance = AsyncMock()
            mock_instance.get.side_effect = [mock_init_response, mock_user_response]
            mock_instance.post.return_value = mock_login_response
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.__aexit__.return_value = None
            mock_client.return_value = mock_instance
            
            response = client.post(
                "/api/auth/login",
                json={
                    "username": "testuser",
                    "password": "SecurePass123!"
                }
            )
            
            assert response.status_code == 200
            assert "access_token" in response.json()
            assert response.json()["user"]["preferred_username"] == "testuser"
    
    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client):
        """Login with invalid credentials should return 401."""
        with patch("app.services.authentik_service.httpx.AsyncClient") as mock_client:
            mock_init_response = MagicMock()
            mock_init_response.status_code = 200
            mock_init_response.json.return_value = {
                "component": "ak-stage-identification"
            }
            
            # Mock access denied
            mock_login_response = MagicMock()
            mock_login_response.status_code = 200
            mock_login_response.json.return_value = {
                "component": "ak-stage-access-denied"
            }
            
            mock_instance = AsyncMock()
            mock_instance.get.return_value = mock_init_response
            mock_instance.post.return_value = mock_login_response
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.__aexit__.return_value = None
            mock_client.return_value = mock_instance
            
            response = client.post(
                "/api/auth/login",
                json={
                    "username": "testuser",
                    "password": "wrongpassword"
                }
            )
            
            assert response.status_code == 401
            assert "Invalid" in response.json()["detail"]
