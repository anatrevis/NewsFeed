import re
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional


class LoginRequest(BaseModel):
    """Schema for login request."""
    username: str = Field(..., min_length=1, description="Username or email")
    password: str = Field(..., min_length=1, description="Password")


class SignupRequest(BaseModel):
    """Schema for signup request."""
    username: str = Field(..., min_length=3, max_length=50, description="Username (lowercase letters and numbers only)")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        # Only allow lowercase letters and numbers
        if not re.match(r'^[a-z0-9]+$', v):
            raise ValueError('Username must contain only lowercase letters and numbers (no spaces, uppercase, or special characters)')
        return v


class UserInfo(BaseModel):
    """Schema for user information."""
    sub: str
    email: Optional[str] = None
    name: Optional[str] = None
    preferred_username: Optional[str] = None


class AuthResponse(BaseModel):
    """Schema for successful authentication response."""
    access_token: str
    token_type: str = "bearer"
    user: UserInfo


class SignupResponse(BaseModel):
    """Schema for successful signup response."""
    message: str
    username: str


class AuthError(BaseModel):
    """Schema for authentication error response."""
    error: str
    detail: str
