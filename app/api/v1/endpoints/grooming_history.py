"""
GroomingHistory API endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.api.deps import get_database, get_current_user
from app.services.grooming_history_service import GroomingHistoryService
from app.schemas.grooming_history import (
    GroomingHistoryCreate,
    GroomingHistoryUpdate,
    GroomingHistoryResponse
)
from app.schemas.home_stats import (
    HomeStatsResponse,
    WeeklySummaryResponse,
    AchievementsResponse
)
from app.schemas.user import UserResponse

router = APIRouter()


@router.post(
    "/",
    response_model=GroomingHistoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create grooming history",
    description="Save a new grooming analysis result from groomify_ml",
    tags=["grooming"]
)
async def create_grooming_history(
    grooming_data: GroomingHistoryCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_database)
) -> GroomingHistoryResponse:
    """
    Create a new grooming history record.
    
    This endpoint saves the complete analysis result from the groomify_ml service,
    including before/after images and full analysis data.
    
    Args:
        grooming_data: Grooming history creation data
        current_user: Current authenticated user
        db: Database session dependency
        
    Returns:
        Created GroomingHistoryResponse object
        
    Raises:
        HTTPException: If validation fails or creation fails
    """
    service = GroomingHistoryService(db)
    return service.create_grooming_history(current_user.id, grooming_data)


@router.get(
    "/",
    response_model=List[GroomingHistoryResponse],
    summary="Get user grooming history",
    description="Get all grooming history for the current user with pagination and sorting",
    tags=["grooming"]
)
def get_user_grooming_history(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return"),
    order_by: str = Query("created_at", description="Field to sort by"),
    order: str = Query("desc", description="Sort direction: asc or desc"),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_database)
) -> List[GroomingHistoryResponse]:
    """
    Get all grooming history for the current user.
    
    Results are paginated and sorted by date (newest first by default).
    
    Args:
        skip: Number of records to skip (pagination offset)
        limit: Maximum number of records to return (1-100)
        order_by: Field to sort by (default: "created_at")
        order: Sort direction "asc" or "desc" (default: "desc")
        current_user: Current authenticated user
        db: Database session dependency
        
    Returns:
        List of GroomingHistoryResponse objects
    """
    service = GroomingHistoryService(db)
    return service.get_user_grooming_history(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        order_by=order_by,
        order=order
    )


@router.get(
    "/stats/home",
    response_model=HomeStatsResponse,
    summary="Get home dashboard statistics",
    description="Get statistics for home dashboard including skin health, streak, and progress",
    tags=["grooming"]
)
def get_home_stats(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_database)
) -> HomeStatsResponse:
    """
    Get home dashboard statistics for the current user.
    
    Returns:
        HomeStatsResponse with calculated statistics
    """
    service = GroomingHistoryService(db)
    return service.get_home_stats(current_user.id)


@router.get(
    "/stats/weekly",
    response_model=WeeklySummaryResponse,
    summary="Get weekly summary",
    description="Get weekly summary statistics including analyses count and improvement",
    tags=["grooming"]
)
def get_weekly_summary(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_database)
) -> WeeklySummaryResponse:
    """
    Get weekly summary statistics for the current user.
    
    Returns:
        WeeklySummaryResponse with weekly statistics
    """
    service = GroomingHistoryService(db)
    return service.get_weekly_summary(current_user.id)


@router.get(
    "/achievements",
    response_model=AchievementsResponse,
    summary="Get user achievements",
    description="Get achievement badges for the current user",
    tags=["grooming"]
)
def get_achievements(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_database)
) -> AchievementsResponse:
    """
    Get achievement badges for the current user.
    
    Returns:
        AchievementsResponse with unlocked badges
    """
    service = GroomingHistoryService(db)
    return service.get_achievements(current_user.id)


@router.get(
    "/{grooming_id}",
    response_model=GroomingHistoryResponse,
    summary="Get grooming history by ID",
    description="Retrieve a specific grooming history record by its ID",
    tags=["grooming"]
)
def get_grooming_history(
    grooming_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_database)
) -> GroomingHistoryResponse:
    """
    Get grooming history by ID.
    
    Users can only access their own grooming history records.
    
    Args:
        grooming_id: Grooming history ID
        current_user: Current authenticated user
        db: Database session dependency
        
    Returns:
        GroomingHistoryResponse object
        
    Raises:
        HTTPException: If grooming history not found or access denied
    """
    service = GroomingHistoryService(db)
    return service.get_grooming_history(grooming_id, current_user.id)


@router.delete(
    "/{grooming_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete grooming history",
    description="Delete a grooming history record by its ID",
    tags=["grooming"]
)
def delete_grooming_history(
    grooming_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_database)
) -> dict:
    """
    Delete a grooming history record.
    
    Users can only delete their own grooming history records.
    
    Args:
        grooming_id: Grooming history ID to delete
        current_user: Current authenticated user
        db: Database session dependency
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If grooming history not found or access denied
    """
    service = GroomingHistoryService(db)
    service.delete_grooming_history(grooming_id, current_user.id)
    return {"message": "Grooming history deleted successfully"}

