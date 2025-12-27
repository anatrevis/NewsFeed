"""Router for authentication endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.schemas.auth import (
    LoginRequest,
    SignupRequest,
    AuthResponse,
    SignupResponse,
    UserInfo,
)
from app.services.authentik_service import (
    AuthentikService,
    AuthentikServiceError,
)
from app.logging_config import get_logger

router = APIRouter()
security = HTTPBearer(auto_error=False)
logger = get_logger(__name__)

# Service instance
authentik_service = AuthentikService()


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    Authenticate user with username and password.
    Returns access token and user info on success.
    """
    logger.info(f"Login attempt | username={request.username}")

    try:
        result = await authentik_service.login(
            username=request.username,
            password=request.password,
        )

        return AuthResponse(
            access_token=result.access_token,
            user=UserInfo(
                sub=result.user.id,
                email=result.user.email,
                name=result.user.name,
                preferred_username=result.user.username,
            ),
        )

    except AuthentikServiceError as e:
        logger.warning(f"Login failed | username={request.username} | error={e.message}")
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message,
        )


@router.post("/signup", response_model=SignupResponse, status_code=201)
async def signup(request: SignupRequest):
    """
    Create a new user account.
    """
    logger.info(f"Signup attempt | username={request.username} | email={request.email}")

    try:
        message = await authentik_service.signup(
            username=request.username,
            email=request.email,
            password=request.password,
        )

        return SignupResponse(
            message=message,
            username=request.username,
        )

    except AuthentikServiceError as e:
        logger.warning(f"Signup failed | username={request.username} | error={e.message}")
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message,
        )


@router.post("/logout", status_code=200)
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Logout user and invalidate the session.
    """
    token = credentials.credentials if credentials else None
    
    logger.info("User logout initiated")
    
    await authentik_service.logout(token)
    
    logger.info("User logged out successfully")
    return {"message": "Logged out successfully"}
