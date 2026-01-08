"""
Analysis schemas for request/response validation.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ChatAnswersRequest(BaseModel):
    """Chat answers from user questions."""
    dailyRoutine: Optional[str] = None
    stylingPreference: Optional[str] = None
    occasions: Optional[List[str]] = Field(default_factory=list)
    concerns: Optional[List[str]] = Field(default_factory=list)
    personalStyle: Optional[List[str]] = Field(default_factory=list)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "dailyRoutine": "Office / Corporate",
                "stylingPreference": "Medium (a few times a week)",
                "occasions": ["Everyday / Office", "Weddings & functions"],
                "concerns": ["Hair fall", "Dandruff"],
                "personalStyle": ["Clean & professional", "Trendy / modern"]
            }
        }
    )


class AnalysisRequest(BaseModel):
    """Request schema for complete analysis."""
    answers: ChatAnswersRequest = Field(..., description="Chat question answers")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "answers": {
                    "dailyRoutine": "Office / Corporate",
                    "stylingPreference": "Medium (a few times a week)",
                    "occasions": ["Everyday / Office"],
                    "concerns": ["Hair fall"],
                    "personalStyle": ["Clean & professional"]
                },
                "metadata": {
                    "timestamp": "2026-01-08T10:30:00Z",
                    "device_info": "Android"
                }
            }
        }
    )


class FaceAnalysisResponse(BaseModel):
    """Face analysis results (placeholder for model integration)."""
    face_shape: Optional[str] = None
    skin_tone: Optional[str] = None
    skin_quality: Optional[str] = Field(None, description="Skin quality assessment (e.g., 'Excellent', 'Good', 'Fair')")
    face_matrix: Optional[Dict[str, Any]] = Field(None, description="Face matrix with measurements and metrics")
    face_metrics: Optional[Dict[str, Any]] = None
    status: str = Field(default="pending", description="Analysis status: pending, completed, failed")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "face_shape": "Oval",
                "skin_tone": "Warm",
                "skin_quality": "Excellent",
                "face_matrix": {
                    "symmetry_score": 0.92,
                    "face_width": 120.5,
                    "face_length": 180.3,
                    "jaw_width": 95.2,
                    "forehead_width": 110.8,
                    "cheekbone_width": 125.6
                },
                "face_metrics": {
                    "symmetry_score": 0.92
                },
                "status": "pending"
            }
        }
    )


class HairstyleRecommendation(BaseModel):
    """Individual hairstyle recommendation."""
    id: int
    name: str
    image_url: str = Field(..., description="URL to hairstyle image")
    description: Optional[str] = None
    confidence_score: Optional[float] = Field(None, description="Confidence score (0.0 to 1.0)")
    suitability_reason: Optional[str] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Classic Side Part",
                "image_url": "/api/v1/uploads/hairstyles/classic_side_part.jpg",
                "description": "Professional and timeless",
                "confidence_score": 0.95,
                "suitability_reason": "Matches your face shape and style preferences"
            }
        }
    )


class StyleRecommendationsResponse(BaseModel):
    """Style recommendations (placeholder for model integration)."""
    best_hairstyles: List[HairstyleRecommendation] = Field(
        default_factory=list, 
        description="Top 3 best hairstyle recommendations"
    )
    hairstyles: List[Dict[str, Any]] = Field(default_factory=list)
    products: List[Dict[str, Any]] = Field(default_factory=list)
    routines: List[Dict[str, Any]] = Field(default_factory=list)
    status: str = Field(default="pending", description="Recommendation status: pending, completed, failed")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "best_hairstyles": [
                    {
                        "id": 1,
                        "name": "Classic Side Part",
                        "image_url": "/api/v1/uploads/hairstyles/classic_side_part.jpg",
                        "description": "Professional and timeless",
                        "confidence_score": 0.95,
                        "suitability_reason": "Matches your face shape"
                    },
                    {
                        "id": 2,
                        "name": "Modern Pompadour",
                        "image_url": "/api/v1/uploads/hairstyles/modern_pompadour.jpg",
                        "confidence_score": 0.88
                    },
                    {
                        "id": 3,
                        "name": "Textured Crop",
                        "image_url": "/api/v1/uploads/hairstyles/textured_crop.jpg",
                        "confidence_score": 0.85
                    }
                ],
                "hairstyles": [],
                "products": [],
                "routines": [],
                "status": "pending"
            }
        }
    )


class PersonalizedInsightsResponse(BaseModel):
    """Personalized insights (placeholder for model integration)."""
    best_styles: List[str] = Field(default_factory=list)
    avoid_styles: List[str] = Field(default_factory=list)
    tips: List[str] = Field(default_factory=list)
    status: str = Field(default="pending", description="Insights status: pending, completed, failed")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "best_styles": [],
                "avoid_styles": [],
                "tips": [],
                "status": "pending"
            }
        }
    )


class AnalysisResponse(BaseModel):
    """Response schema for complete analysis."""
    id: int
    user_id: int
    image_url: str = Field(..., description="URL to access the uploaded image")
    chat_answers: Dict[str, Any]
    face_analysis: FaceAnalysisResponse
    style_recommendations: StyleRecommendationsResponse
    personalized_insights: PersonalizedInsightsResponse
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "user_id": 5,
                "image_url": "/api/v1/uploads/analyses/user_5_analysis_123.jpg",
                "chat_answers": {
                    "dailyRoutine": "Office / Corporate",
                    "stylingPreference": "Medium (a few times a week)"
                },
                "face_analysis": {
                    "status": "pending"
                },
                "style_recommendations": {
                    "status": "pending"
                },
                "personalized_insights": {
                    "status": "pending"
                },
                "created_at": "2026-01-08T10:30:00Z",
                "updated_at": "2026-01-08T10:30:00Z"
            }
        }
    )

