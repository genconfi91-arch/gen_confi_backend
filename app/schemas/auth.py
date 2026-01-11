"""
Authentication Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.schemas.user import UserResponse


class SignupRequest(BaseModel):
    """Schema for user signup request."""
    name: str = Field(..., min_length=1, max_length=255, description="User full name", examples=["John Doe"])
    email: EmailStr = Field(..., description="User email address", examples=["john.doe@example.com"])
    phone: str = Field(..., min_length=1, max_length=20, description="User phone number", examples=["1234567890"])
    password: str = Field(..., min_length=6, description="User password (minimum 6 characters)", examples=["password123"])
    gender: str = Field(..., description="User gender (Male/Female/Other)", examples=["Male"])
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "1234567890",
                "password": "password123",
                "gender": "Male"
            }
        }
    )


class LoginRequest(BaseModel):
    """Schema for user login request."""
    email: EmailStr = Field(..., description="User email address", examples=["john.doe@example.com"])
    password: str = Field(..., description="User password", examples=["password123"])
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "john.doe@example.com",
                "password": "password123"
            }
        }
    )


class ForgotPasswordRequest(BaseModel):
    """Schema for forgot password request."""
    email: EmailStr = Field(..., description="User email address")


class ResetPasswordRequest(BaseModel):
    """Schema for reset password request."""
    token: str = Field(..., description="Reset token")
    new_password: str = Field(..., min_length=6, description="New password")


class ChangePasswordRequest(BaseModel):
    """Schema for change password request."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=6, description="New password")


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


class LoginResponse(BaseModel):
    """Schema for login/signup response."""
    access_token: str = Field(..., description="JWT access token", examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."])
    token_type: str = Field(default="bearer", description="Token type", examples=["bearer"])
    user: UserResponse = Field(..., description="User information")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJqb2huQGV4YW1wbGUuY29tIn0...",
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "email": "john.doe@example.com",
                    "name": "John Doe",
                    "phone": "1234567890",
                    "role": "client"
                }
            }
        }
    )
