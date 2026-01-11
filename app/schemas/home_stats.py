"""
Home stats schemas for dashboard statistics.
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class HomeStatsResponse(BaseModel):
    """Home dashboard statistics response."""
    skin_health_score: Optional[float] = Field(
        None,
        description="Latest skin health score (0-100)",
        ge=0,
        le=100
    )
    daily_streak: int = Field(
        0,
        description="Current daily streak count",
        ge=0
    )
    progress_percentage: Optional[float] = Field(
        None,
        description="Progress percentage compared to previous analysis",
        ge=-100,
        le=100
    )
    total_analyses: int = Field(
        0,
        description="Total number of analyses completed",
        ge=0
    )
    latest_analysis_date: Optional[datetime] = Field(
        None,
        description="Date of latest analysis"
    )


class WeeklySummaryResponse(BaseModel):
    """Weekly summary statistics."""
    analyses_count: int = Field(
        0,
        description="Number of analyses this week",
        ge=0
    )
    average_skin_health: Optional[float] = Field(
        None,
        description="Average skin health score this week",
        ge=0,
        le=100
    )
    improvement_percentage: Optional[float] = Field(
        None,
        description="Improvement percentage compared to previous week",
        ge=-100,
        le=100
    )
    week_start_date: datetime = Field(
        ...,
        description="Start date of the week"
    )
    week_end_date: datetime = Field(
        ...,
        description="End date of the week"
    )


class AchievementBadge(BaseModel):
    """Achievement badge model."""
    id: str = Field(..., description="Badge identifier")
    title: str = Field(..., description="Badge title")
    description: str = Field(..., description="Badge description")
    icon: str = Field(..., description="Badge icon name")
    unlocked: bool = Field(False, description="Whether badge is unlocked")
    unlocked_at: Optional[datetime] = Field(None, description="When badge was unlocked")


class AchievementsResponse(BaseModel):
    """User achievements response."""
    badges: List[AchievementBadge] = Field(
        default_factory=list,
        description="List of achievement badges"
    )
    total_unlocked: int = Field(
        0,
        description="Total number of unlocked badges",
        ge=0
    )

