"""
GroomingHistory Pydantic schemas for request/response validation.
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator


class GroomingHistoryBase(BaseModel):
    """Base grooming history schema with common fields."""
    analysis_data: Dict[str, Any] = Field(
        ...,
        description="Complete groomify_ml API response as JSON object"
    )
    before_image_url: Optional[str] = Field(
        None,
        max_length=10000,
        description="Before image URL or base64 encoded string"
    )
    after_image_url: Optional[str] = Field(
        None,
        max_length=10000,
        description="After image URL or base64 encoded string"
    )
    status: str = Field(
        default="pending",
        description="Analysis status: success, partial_success, error"
    )
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status value."""
        allowed_statuses = ["success", "partial_success", "error", "pending"]
        if v not in allowed_statuses:
            raise ValueError(f"Status must be one of: {', '.join(allowed_statuses)}")
        return v


class GroomingHistoryCreate(GroomingHistoryBase):
    """Schema for creating a new grooming history record."""
    pass


class GroomingHistoryUpdate(BaseModel):
    """Schema for updating grooming history (all fields optional)."""
    analysis_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Complete groomify_ml API response as JSON object"
    )
    before_image_url: Optional[str] = Field(
        None,
        max_length=10000,
        description="Before image URL or base64 encoded string"
    )
    after_image_url: Optional[str] = Field(
        None,
        max_length=10000,
        description="After image URL or base64 encoded string"
    )
    status: Optional[str] = Field(
        None,
        description="Analysis status: success, partial_success, error"
    )
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate status value."""
        if v is None:
            return v
        allowed_statuses = ["success", "partial_success", "error", "pending"]
        if v not in allowed_statuses:
            raise ValueError(f"Status must be one of: {', '.join(allowed_statuses)}")
        return v


class GroomingHistoryResponse(GroomingHistoryBase):
    """Schema for grooming history API response."""
    id: int = Field(..., description="Grooming history ID")
    user_id: int = Field(..., description="User ID who owns this grooming history")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = ConfigDict(from_attributes=True)


class GroomingHistorySummary(BaseModel):
    """Schema for grooming history summary (for list endpoints)."""
    id: int = Field(..., description="Grooming history ID")
    user_id: int = Field(..., description="User ID")
    status: str = Field(..., description="Analysis status")
    face_shape: Optional[str] = Field(None, description="Detected face shape")
    gender: Optional[str] = Field(None, description="User gender")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = ConfigDict(from_attributes=True)

