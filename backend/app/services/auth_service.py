import httpx
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import get_settings

settings = get_settings()
security = HTTPBearer(auto_error=False)


class AuthService:
    """Service for Authentik token validation."""

    def __init__(self):
        self.authentik_url = settings.authentik_url

    async def validate_oauth_token(self, token: str) -> dict | None:
        """
        Validate OAuth token (JWT) with Authentik's userinfo endpoint.
        """
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.authentik_url}/application/o/userinfo/"
                response = await client.get(
                    url,
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
                return None
        except Exception:
            return None

    async def validate_api_token(self, token: str) -> dict | None:
        """
        Validate Authentik API token.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.authentik_url}/api/v3/core/users/me/",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    user_data = data.get("user", data)
                    return {
                        "sub": str(user_data.get("pk", "")),
                        "email": user_data.get("email", ""),
                        "name": user_data.get("name", ""),
                        "preferred_username": user_data.get("username", ""),
                    }
                return None
        except Exception:
            return None

    async def validate_token(self, token: str) -> dict | None:
        """
        Validate any token type (OAuth JWT or API token).
        JWT tokens start with "eyJ" (base64 for {"alg":...)
        """
        if token.startswith("eyJ"):
            return await self.validate_oauth_token(token)
        return await self.validate_api_token(token)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Require authentication. Returns user info or raises 401.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    auth_service = AuthService()
    user_info = await auth_service.validate_token(credentials.credentials)
    
    if user_info is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_info

