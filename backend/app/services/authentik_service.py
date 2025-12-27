"""Service for interacting with Authentik authentication flows."""

import httpx
import jwt
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional

from app.config import get_settings
from app.logging_config import get_logger

settings = get_settings()
logger = get_logger(__name__)


class AuthentikServiceError(Exception):
    """Base exception for Authentik service errors."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationError(AuthentikServiceError):
    """Invalid credentials."""
    def __init__(self, message: str = "Invalid username or password"):
        super().__init__(message, status_code=401)


class RegistrationError(AuthentikServiceError):
    """Registration failed."""
    def __init__(self, message: str = "Registration failed", status_code: int = 400):
        super().__init__(message, status_code=status_code)


class ConflictError(AuthentikServiceError):
    """Resource already exists (duplicate username/email)."""
    def __init__(self, message: str = "Username or email already exists"):
        super().__init__(message, status_code=409)


class ServiceUnavailableError(AuthentikServiceError):
    """Authentik service unavailable."""
    def __init__(self, message: str = "Authentication service unavailable"):
        super().__init__(message, status_code=503)


class MFARequiredError(AuthentikServiceError):
    """Multi-factor authentication required."""
    def __init__(self, message: str = "Multi-factor authentication is required but not supported"):
        super().__init__(message, status_code=400)


@dataclass
class UserData:
    """User data from Authentik."""
    id: str
    username: str
    email: str
    name: str


@dataclass
class AuthResult:
    """Result of successful authentication."""
    access_token: str
    user: UserData


class AuthentikService:
    """Service for Authentik authentication operations."""

    TIMEOUT_SECONDS = 15.0
    TOKEN_EXPIRY_HOURS = 24

    def __init__(self):
        self.base_url = settings.authentik_url
        self.client_id = settings.authentik_client_id

    def _create_app_token(self, user_data: dict) -> str:
        """Create a JWT token for our application."""
        token_payload = {
            "sub": str(user_data.get("pk", user_data.get("sub", ""))),
            "email": user_data.get("email", ""),
            "name": user_data.get("name", ""),
            "preferred_username": user_data.get("username", user_data.get("preferred_username", "")),
            "exp": datetime.utcnow() + timedelta(hours=self.TOKEN_EXPIRY_HOURS),
            "iat": datetime.utcnow(),
        }
        return jwt.encode(token_payload, self.client_id, algorithm="HS256")

    async def login(self, username: str, password: str) -> AuthResult:
        """
        Authenticate user with username and password using Authentik's flow executor.
        
        Args:
            username: User's username
            password: User's password
            
        Returns:
            AuthResult with access token and user data
            
        Raises:
            AuthenticationError: Invalid credentials
            MFARequiredError: MFA required but not supported
            ServiceUnavailableError: Authentik unavailable
        """
        logger.debug(f"Authenticating user: {username}")

        try:
            async with httpx.AsyncClient(
                timeout=self.TIMEOUT_SECONDS,
                follow_redirects=True,
                cookies=httpx.Cookies()
            ) as client:
                # Step 1: Initialize the authentication flow
                flow_init = await client.get(
                    f"{self.base_url}/api/v3/flows/executor/default-authentication-flow/",
                    params={"query": ""},
                )

                if flow_init.status_code != 200:
                    logger.error(f"Auth flow init failed | status={flow_init.status_code}")
                    raise ServiceUnavailableError()

                flow_data = flow_init.json()
                component = flow_data.get("component", "ak-stage-identification")
                logger.debug(f"Auth flow component: {component}")

                # Step 2: Submit credentials based on the flow stage
                if component == "ak-stage-identification":
                    submit_response = await client.post(
                        f"{self.base_url}/api/v3/flows/executor/default-authentication-flow/",
                        json={
                            "component": "ak-stage-identification",
                            "uid_field": username,
                            "password": password,
                        },
                        params={"query": ""},
                    )
                    response_data = submit_response.json()

                    # If identification stage passes to password stage
                    if response_data.get("component") == "ak-stage-password":
                        logger.debug("Proceeding to password stage")
                        submit_response = await client.post(
                            f"{self.base_url}/api/v3/flows/executor/default-authentication-flow/",
                            json={
                                "component": "ak-stage-password",
                                "password": password,
                            },
                            params={"query": ""},
                        )
                        response_data = submit_response.json()
                else:
                    response_data = flow_data

                # Check for errors
                if response_data.get("component") == "ak-stage-access-denied":
                    logger.warning(f"Login denied | username={username}")
                    raise AuthenticationError()

                if "response_errors" in response_data:
                    errors = response_data.get("response_errors", {})
                    logger.warning(f"Login errors | username={username} | errors={errors}")
                    if "non_field_errors" in errors:
                        error_list = errors["non_field_errors"]
                        if error_list:
                            raise AuthenticationError(
                                error_list[0].get("string", "Authentication failed")
                            )
                    raise AuthenticationError()

                # Check if MFA is required
                if response_data.get("component") in ["ak-stage-authenticator-validate", "ak-stage-authenticator-totp"]:
                    logger.warning(f"MFA required | username={username}")
                    raise MFARequiredError()

                # Check for successful redirect (login complete)
                if response_data.get("type") == "redirect" or response_data.get("component") == "xak-flow-redirect":
                    me_response = await client.get(
                        f"{self.base_url}/api/v3/core/users/me/",
                    )

                    if me_response.status_code == 200:
                        user_data = me_response.json().get("user", {})
                        access_token = self._create_app_token(user_data)

                        logger.info(f"Login successful | username={username} | user_id={user_data.get('pk')}")

                        return AuthResult(
                            access_token=access_token,
                            user=UserData(
                                id=str(user_data.get("pk", "")),
                                username=user_data.get("username", ""),
                                email=user_data.get("email", ""),
                                name=user_data.get("name", ""),
                            ),
                        )

                logger.warning(f"Login failed - unexpected response | username={username}")
                raise AuthenticationError()

        except httpx.TimeoutException:
            logger.error(f"Auth service timeout | username={username}")
            raise ServiceUnavailableError("Authentication service is temporarily unavailable")
        except httpx.RequestError as e:
            logger.error(f"Auth service connection error | username={username} | error={str(e)}")
            raise ServiceUnavailableError("Unable to connect to authentication service")
        except AuthentikServiceError:
            raise
        except Exception as e:
            logger.error(f"Unexpected login error | username={username} | error={str(e)}", exc_info=True)
            raise AuthentikServiceError("An unexpected error occurred during login")

    async def signup(self, username: str, email: str, password: str) -> str:
        """
        Create a new user account using Authentik's enrollment flow.
        
        Args:
            username: Desired username
            email: User's email
            password: User's password
            
        Returns:
            Success message
            
        Raises:
            ConflictError: Username or email already exists
            RegistrationError: Invalid registration data
            ServiceUnavailableError: Authentik unavailable
        """
        logger.debug(f"Registering user: {username}")

        try:
            async with httpx.AsyncClient(
                timeout=self.TIMEOUT_SECONDS,
                follow_redirects=True,
                cookies=httpx.Cookies()
            ) as client:
                # Step 1: Initialize the enrollment flow
                flow_init = await client.get(
                    f"{self.base_url}/api/v3/flows/executor/newsfeed-enrollment/",
                    params={"query": ""},
                )

                if flow_init.status_code == 404:
                    logger.error("Enrollment flow not found")
                    raise ServiceUnavailableError("User registration is not configured")

                if flow_init.status_code != 200:
                    logger.error(f"Enrollment init failed | status={flow_init.status_code}")
                    raise ServiceUnavailableError("Registration service unavailable")

                flow_data = flow_init.json()
                logger.debug(f"Enrollment flow component: {flow_data.get('component')}")

                # Check if access is denied immediately
                if flow_data.get("component") == "ak-stage-access-denied":
                    logger.warning("Registration disabled")
                    raise RegistrationError("Registration is currently disabled", status_code=403)

                # Step 2: Submit user registration data
                register_response = await client.post(
                    f"{self.base_url}/api/v3/flows/executor/newsfeed-enrollment/",
                    json={
                        "component": flow_data.get("component", "ak-stage-prompt"),
                        "username": username,
                        "email": email,
                        "password": password,
                        "password_repeat": password,
                    },
                    params={"query": ""},
                )

                response_data = register_response.json()

                # Check for validation errors
                if "response_errors" in response_data:
                    errors = response_data.get("response_errors", {})
                    logger.warning(f"Signup validation errors | username={username} | errors={errors}")

                    if "username" in errors:
                        error_list = errors["username"]
                        if error_list:
                            raise ConflictError(error_list[0].get("string", "Username is already taken"))

                    if "email" in errors:
                        error_list = errors["email"]
                        if error_list:
                            raise ConflictError(error_list[0].get("string", "Email is already registered"))

                    if "password" in errors:
                        error_list = errors["password"]
                        if error_list:
                            raise RegistrationError(error_list[0].get("string", "Password does not meet requirements"))

                    if "non_field_errors" in errors:
                        error_list = errors["non_field_errors"]
                        if error_list:
                            raise RegistrationError(error_list[0].get("string", "Registration failed"))

                    raise RegistrationError("Invalid registration data")

                # Check for access denied (can also indicate duplicate user)
                if response_data.get("component") == "ak-stage-access-denied":
                    error_msg = response_data.get("error_message", "")
                    logger.warning(f"Signup access denied | username={username} | error={error_msg}")
                    if "update user" in error_msg.lower() or "already" in error_msg.lower():
                        raise ConflictError("Username or email is already taken")
                    raise RegistrationError(error_msg or "Registration is currently disabled", status_code=403)

                # Success - flow completed (redirect)
                if response_data.get("type") == "redirect" or response_data.get("component") == "xak-flow-redirect":
                    logger.info(f"Signup successful | username={username} | email={email}")
                    return "Account created successfully. You can now log in."

                # Unexpected state
                logger.error(f"Signup incomplete | username={username} | response={response_data}")
                raise RegistrationError("Registration process incomplete")

        except httpx.TimeoutException:
            logger.error(f"Registration service timeout | username={username}")
            raise ServiceUnavailableError("Registration service is temporarily unavailable")
        except httpx.RequestError as e:
            logger.error(f"Registration service connection error | username={username} | error={str(e)}")
            raise ServiceUnavailableError("Unable to connect to registration service")
        except AuthentikServiceError:
            raise
        except Exception as e:
            logger.error(f"Unexpected signup error | username={username} | error={str(e)}", exc_info=True)
            raise AuthentikServiceError("An unexpected error occurred during registration")

    async def logout(self, token: Optional[str] = None) -> None:
        """
        Logout user and attempt to revoke the token.
        
        Args:
            token: The access token to revoke (optional)
        """
        if not token:
            logger.debug("Logout without token")
            return

        logger.debug("Attempting token revocation")

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(
                    f"{self.base_url}/application/o/revoke/",
                    data={
                        "token": token,
                        "client_id": self.client_id,
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                logger.debug("Token revocation sent")
        except Exception as e:
            # Token revocation is best-effort, don't fail logout
            logger.debug(f"Token revocation failed (non-critical): {str(e)}")

