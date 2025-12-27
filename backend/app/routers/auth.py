import httpx
import jwt
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import get_settings
from app.schemas.auth import (
    LoginRequest,
    SignupRequest,
    AuthResponse,
    SignupResponse,
    UserInfo,
)

router = APIRouter()
settings = get_settings()
security = HTTPBearer(auto_error=False)


def create_app_token(user_data: dict) -> str:
    """Create a JWT token for our application."""
    token_payload = {
        "sub": str(user_data.get("pk", user_data.get("sub", ""))),
        "email": user_data.get("email", ""),
        "name": user_data.get("name", ""),
        "preferred_username": user_data.get("username", user_data.get("preferred_username", "")),
        "exp": datetime.utcnow() + timedelta(hours=24),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(token_payload, settings.authentik_client_id, algorithm="HS256")


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    Authenticate user with username and password using Authentik's flow executor.
    Returns access token and user info on success.
    """
    try:
        # Use cookies to maintain session across requests
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True, cookies=httpx.Cookies()) as client:
            # Step 1: Initialize the authentication flow
            flow_init = await client.get(
                f"{settings.authentik_url}/api/v3/flows/executor/default-authentication-flow/",
                params={"query": ""},
            )
            
            if flow_init.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Authentication service unavailable",
                )
            
            flow_data = flow_init.json()
            component = flow_data.get("component", "ak-stage-identification")
            
            # Step 2: Submit credentials based on the flow stage
            if component == "ak-stage-identification":
                # Combined identification and password
                submit_response = await client.post(
                    f"{settings.authentik_url}/api/v3/flows/executor/default-authentication-flow/",
                    json={
                        "component": "ak-stage-identification",
                        "uid_field": request.username,
                        "password": request.password,
                    },
                    params={"query": ""},
                )
                response_data = submit_response.json()
                
                # If identification stage passes to password stage
                if response_data.get("component") == "ak-stage-password":
                    submit_response = await client.post(
                        f"{settings.authentik_url}/api/v3/flows/executor/default-authentication-flow/",
                        json={
                            "component": "ak-stage-password",
                            "password": request.password,
                        },
                        params={"query": ""},
                    )
                    response_data = submit_response.json()
            else:
                response_data = flow_data
            
            # Check for errors
            if response_data.get("component") == "ak-stage-access-denied":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid username or password",
                )
            
            if "response_errors" in response_data:
                errors = response_data.get("response_errors", {})
                if "non_field_errors" in errors:
                    error_list = errors["non_field_errors"]
                    if error_list:
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=error_list[0].get("string", "Authentication failed"),
                        )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid username or password",
                )
            
            # Check if we need MFA or other stages
            if response_data.get("component") in ["ak-stage-authenticator-validate", "ak-stage-authenticator-totp"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Multi-factor authentication is required but not supported in this flow",
                )
            
            # Check for successful redirect (login complete)
            if response_data.get("type") == "redirect" or response_data.get("component") == "xak-flow-redirect":
                # Get user info from the authenticated session
                me_response = await client.get(
                    f"{settings.authentik_url}/api/v3/core/users/me/",
                )
                
                if me_response.status_code == 200:
                    user_data = me_response.json().get("user", {})
                    access_token = create_app_token(user_data)
                    
                    return AuthResponse(
                        access_token=access_token,
                        user=UserInfo(
                            sub=str(user_data.get("pk", "")),
                            email=user_data.get("email"),
                            name=user_data.get("name"),
                            preferred_username=user_data.get("username"),
                        ),
                    )
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )
            
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service is temporarily unavailable",
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to connect to authentication service",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during login",
        )


@router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignupRequest):
    """
    Create a new user account using Authentik's enrollment flow.
    """
    try:
        # Use cookies to maintain session across requests
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True, cookies=httpx.Cookies()) as client:
            # Step 1: Initialize the enrollment flow
            flow_init = await client.get(
                f"{settings.authentik_url}/api/v3/flows/executor/newsfeed-enrollment/",
                params={"query": ""},
            )
            
            if flow_init.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="User registration is not configured",
                )
            
            if flow_init.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Registration service unavailable",
                )
            
            flow_data = flow_init.json()
            
            # Check if access is denied immediately
            if flow_data.get("component") == "ak-stage-access-denied":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Registration is currently disabled",
                )
            
            # Step 2: Submit user registration data
            register_response = await client.post(
                f"{settings.authentik_url}/api/v3/flows/executor/newsfeed-enrollment/",
                json={
                    "component": flow_data.get("component", "ak-stage-prompt"),
                    "username": request.username,
                    "email": request.email,
                    "password": request.password,
                    "password_repeat": request.password,
                },
                params={"query": ""},
            )
            
            response_data = register_response.json()
            
            # Check for validation errors
            if "response_errors" in response_data:
                errors = response_data.get("response_errors", {})
                
                # Check for specific field errors
                if "username" in errors:
                    error_list = errors["username"]
                    if error_list:
                        raise HTTPException(
                            status_code=status.HTTP_409_CONFLICT,
                            detail=error_list[0].get("string", "Username is already taken"),
                        )
                
                if "email" in errors:
                    error_list = errors["email"]
                    if error_list:
                        raise HTTPException(
                            status_code=status.HTTP_409_CONFLICT,
                            detail=error_list[0].get("string", "Email is already registered"),
                        )
                
                if "password" in errors:
                    error_list = errors["password"]
                    if error_list:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=error_list[0].get("string", "Password does not meet requirements"),
                        )
                
                if "non_field_errors" in errors:
                    error_list = errors["non_field_errors"]
                    if error_list:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=error_list[0].get("string", "Registration failed"),
                        )
                
                # Generic error
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid registration data",
                )
            
            # Check for access denied (can also indicate duplicate user)
            if response_data.get("component") == "ak-stage-access-denied":
                error_msg = response_data.get("error_message", "")
                if "update user" in error_msg.lower() or "already" in error_msg.lower():
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Username or email is already taken",
                    )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=error_msg or "Registration is currently disabled",
                )
            
            # Success - flow completed (redirect)
            if response_data.get("type") == "redirect" or response_data.get("component") == "xak-flow-redirect":
                return SignupResponse(
                    message="Account created successfully. You can now log in.",
                    username=request.username,
                )
            
            # If we're still in another stage, something unexpected happened
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration process incomplete",
            )
            
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Registration service is temporarily unavailable",
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to connect to registration service",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during registration",
        )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Logout user and invalidate the session.
    """
    if not credentials:
        return {"message": "Logged out successfully"}
    
    token = credentials.credentials
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Try to revoke the token
            await client.post(
                f"{settings.authentik_url}/application/o/revoke/",
                data={
                    "token": token,
                    "client_id": settings.authentik_client_id,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
    except Exception:
        pass  # Ignore revocation errors
    
    return {"message": "Logged out successfully"}
