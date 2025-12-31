"""
Authentication Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.schemas.user import UserResponse


class SignupRequest(BaseModel):
    """Schema for user signup request."""
    name: str = Field(..., min_length=1, max_length=255, description="User full name")
    email: EmailStr = Field(..., description="User email address")
    phone: str = Field(..., min_length=1, max_length=20, description="User phone number")
    password: str = Field(..., min_length=6, description="User password (minimum 6 characters)")


class LoginRequest(BaseModel):
    """Schema for user login request."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


class LoginResponse(BaseModel):
    """Schema for login/signup response."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: UserResponse = Field(..., description="User information")

