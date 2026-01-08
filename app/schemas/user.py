"""
User Pydantic schemas for request/response validation.
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr = Field(..., description="User email address")
    name: str = Field(..., min_length=1, max_length=255, description="User full name")
    phone: Optional[str] = Field(None, max_length=20, description="User phone number")
    role: UserRole = Field(default=UserRole.CLIENT, description="User role")
    avatar_url: Optional[str] = Field(None, max_length=500, description="Profile photo URL or path")
    gender: Optional[str] = Field(None, max_length=20, description="User gender")


class UserCreate(UserBase):
    """Schema for creating a new user."""
    pass


class UserUpdate(BaseModel):
    """Schema for updating an existing user."""
    email: Optional[EmailStr] = Field(None, description="User email address")
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="User full name")
    phone: Optional[str] = Field(None, max_length=20, description="User phone number")
    role: Optional[UserRole] = Field(None, description="User role")
    avatar_url: Optional[str] = Field(None, max_length=500, description="Profile photo URL or path")
    gender: Optional[str] = Field(None, max_length=20, description="User gender")


class UserInDB(UserBase):
    """Schema for user data in database."""
    id: int = Field(..., description="User ID")
    
    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserInDB):
    """Schema for user API response (excludes password)."""
    pass


class AvatarUpdate(BaseModel):
    """Schema for updating only the user avatar."""
    avatar_url: str = Field(..., description="The URL or Path of the avatar")

