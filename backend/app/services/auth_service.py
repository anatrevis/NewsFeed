import jwt
import httpx
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import get_settings

settings = get_settings()
security = HTTPBearer(auto_error=False)


class AuthService:
    """Service for token validation."""

    def __init__(self):
        self.authentik_url = settings.authentik_url
        self.jwt_secret = settings.authentik_client_id  # Same secret used in auth router

    def validate_app_jwt(self, token: str) -> dict | None:
        """
        Validate our application's JWT tokens.
        """
        try:
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=["HS256"],
            )
            return {
                "sub": payload.get("sub", ""),
                "email": payload.get("email", ""),
                "name": payload.get("name", ""),
                "preferred_username": payload.get("preferred_username", ""),
            }
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    async def validate_authentik_token(self, token: str) -> dict | None:
        """
        Validate token with Authentik's userinfo endpoint (fallback).
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.authentik_url}/application/o/userinfo/",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
                return None
        except Exception:
            return None

    async def validate_token(self, token: str) -> dict | None:
        """
        Validate token - first try our app JWT, then Authentik.
        """
        # First, try to validate as our app's JWT
        user_info = self.validate_app_jwt(token)
        if user_info:
            return user_info
        
        # Fallback to Authentik validation
        return await self.validate_authentik_token(token)


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
