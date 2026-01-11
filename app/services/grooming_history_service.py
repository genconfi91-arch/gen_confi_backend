"""
GroomingHistory service for business logic.
"""
from typing import List, Optional
from datetime import datetime, timedelta, date
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.grooming_history_repository import GroomingHistoryRepository
from app.schemas.grooming_history import (
    GroomingHistoryCreate,
    GroomingHistoryUpdate,
    GroomingHistoryResponse
)
from app.schemas.home_stats import (
    HomeStatsResponse,
    WeeklySummaryResponse,
    AchievementBadge,
    AchievementsResponse
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class GroomingHistoryService:
    """Service for grooming history operations."""
    
    def __init__(self, db: Session):
        """
        Initialize service with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.repository = GroomingHistoryRepository(db)
    
    def create_grooming_history(
        self,
        user_id: int,
        grooming_data: GroomingHistoryCreate
    ) -> GroomingHistoryResponse:
        """
        Create a new grooming history record.
        
        Args:
            user_id: The user ID who owns this grooming history
            grooming_data: Grooming history creation data
            
        Returns:
            Created GroomingHistoryResponse object
            
        Raises:
            HTTPException: If validation fails or creation fails
        """
        try:
            # Validate analysis_data structure
            if not isinstance(grooming_data.analysis_data, dict):
                raise ValueError("analysis_data must be a JSON object")
            
            # Extract status from analysis_data if not provided
            if not grooming_data.status or grooming_data.status == "pending":
                status_from_data = grooming_data.analysis_data.get("status")
                if status_from_data:
                    grooming_data.status = status_from_data
            
            # Create grooming history
            db_grooming = self.repository.create(user_id, grooming_data)
            return GroomingHistoryResponse.model_validate(db_grooming)
            
        except Exception as e:
            logger.error(f"Failed to create grooming history: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create grooming history: {str(e)}"
            )
    
    def get_grooming_history(
        self,
        grooming_id: int,
        user_id: int
    ) -> GroomingHistoryResponse:
        """
        Get grooming history by ID with user authorization check.
        
        Args:
            grooming_id: The grooming history ID
            user_id: The user ID requesting the data (for authorization)
            
        Returns:
            GroomingHistoryResponse object
            
        Raises:
            HTTPException: If grooming history not found or access denied
        """
        db_grooming = self.repository.get_by_id(grooming_id)
        
        if not db_grooming:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grooming history not found"
            )
        
        # Authorization check: user can only access their own grooming history
        if db_grooming.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this grooming history"
            )
        
        return GroomingHistoryResponse.model_validate(db_grooming)
    
    def get_user_grooming_history(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
        order_by: str = "created_at",
        order: str = "desc"
    ) -> List[GroomingHistoryResponse]:
        """
        Get all grooming history for a user with pagination and sorting.
        
        Args:
            user_id: The user ID to get grooming history for
            skip: Number of records to skip
            limit: Maximum number of records to return (max 100)
            order_by: Field to sort by (default: "created_at")
            order: Sort direction "asc" or "desc" (default: "desc")
            
        Returns:
            List of GroomingHistoryResponse objects
        """
        # Validate limit
        if limit > 100:
            limit = 100
        if limit < 1:
            limit = 10
        
        # Validate order
        if order.lower() not in ["asc", "desc"]:
            order = "desc"
        
        db_groomings = self.repository.get_by_user_id(
            user_id=user_id,
            skip=skip,
            limit=limit,
            order_by=order_by,
            order=order
        )
        
        return [GroomingHistoryResponse.model_validate(g) for g in db_groomings]
    
    def update_grooming_history(
        self,
        grooming_id: int,
        user_id: int,
        grooming_data: GroomingHistoryUpdate
    ) -> GroomingHistoryResponse:
        """
        Update an existing grooming history record with authorization check.
        
        Args:
            grooming_id: The grooming history ID to update
            user_id: The user ID requesting the update (for authorization)
            grooming_data: Grooming history update data
            
        Returns:
            Updated GroomingHistoryResponse object
            
        Raises:
            HTTPException: If grooming history not found or access denied
        """
        # Check if grooming history exists and user has access
        db_grooming = self.repository.get_by_id(grooming_id)
        
        if not db_grooming:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grooming history not found"
            )
        
        # Authorization check
        if db_grooming.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this grooming history"
            )
        
        # Update grooming history
        updated_grooming = self.repository.update(grooming_id, grooming_data)
        
        if not updated_grooming:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update grooming history"
            )
        
        return GroomingHistoryResponse.model_validate(updated_grooming)
    
    def delete_grooming_history(
        self,
        grooming_id: int,
        user_id: int
    ) -> bool:
        """
        Delete a grooming history record with authorization check.
        
        Args:
            grooming_id: The grooming history ID to delete
            user_id: The user ID requesting the deletion (for authorization)
            
        Returns:
            True if deleted successfully
            
        Raises:
            HTTPException: If grooming history not found or access denied
        """
        # Check if grooming history exists and user has access
        db_grooming = self.repository.get_by_id(grooming_id)
        
        if not db_grooming:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grooming history not found"
            )
        
        # Authorization check
        if db_grooming.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this grooming history"
            )
        
        # Delete grooming history
        deleted = self.repository.delete(grooming_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete grooming history"
            )
        
        return True
    
    def get_home_stats(self, user_id: int) -> HomeStatsResponse:
        """
        Get home dashboard statistics for a user.
        
        Args:
            user_id: The user ID to get stats for
            
        Returns:
            HomeStatsResponse with calculated statistics
        """
        try:
            # Get latest and previous analyses
            latest = self.repository.get_latest_by_user_id(user_id)
            previous = self.repository.get_previous_by_user_id(user_id)
            total_count = self.repository.count_by_user_id(user_id)
            
            # Calculate skin health score from latest analysis
            skin_health_score = None
            if latest and latest.analysis_data:
                skin_data = latest.analysis_data.get("skin") or latest.analysis_data.get("features", {}).get("skin")
                if skin_data and isinstance(skin_data, dict):
                    ita_score = skin_data.get("ita_score")
                    if ita_score is not None:
                        # Convert ITA score (-50 to 60) to percentage (0-100)
                        # Normalize: (ita_score + 50) / 110 * 100
                        normalized = ((float(ita_score) + 50) / 110) * 100
                        skin_health_score = max(0, min(100, normalized))
            
            # Calculate daily streak
            daily_streak = self._calculate_daily_streak(user_id)
            
            # Calculate progress percentage
            progress_percentage = None
            if latest and previous:
                latest_skin = latest.analysis_data.get("skin") or latest.analysis_data.get("features", {}).get("skin")
                previous_skin = previous.analysis_data.get("skin") or previous.analysis_data.get("features", {}).get("skin")
                
                if latest_skin and previous_skin and isinstance(latest_skin, dict) and isinstance(previous_skin, dict):
                    latest_ita = latest_skin.get("ita_score")
                    previous_ita = previous_skin.get("ita_score")
                    
                    if latest_ita is not None and previous_ita is not None:
                        latest_normalized = ((float(latest_ita) + 50) / 110) * 100
                        previous_normalized = ((float(previous_ita) + 50) / 110) * 100
                        
                        if previous_normalized > 0:
                            progress_percentage = ((latest_normalized - previous_normalized) / previous_normalized) * 100
            
            return HomeStatsResponse(
                skin_health_score=skin_health_score,
                daily_streak=daily_streak,
                progress_percentage=progress_percentage,
                total_analyses=total_count,
                latest_analysis_date=latest.created_at if latest else None
            )
            
        except Exception as e:
            logger.error(f"Failed to get home stats: {e}", exc_info=True)
            # Return default stats on error
            return HomeStatsResponse(
                skin_health_score=None,
                daily_streak=0,
                progress_percentage=None,
                total_analyses=0,
                latest_analysis_date=None
            )
    
    def _calculate_daily_streak(self, user_id: int) -> int:
        """
        Calculate daily streak based on consecutive days with analyses.
        
        Args:
            user_id: The user ID to calculate streak for
            
        Returns:
            Number of consecutive days with analyses
        """
        try:
            distinct_dates = self.repository.get_distinct_dates_by_user_id(user_id)
            
            if not distinct_dates:
                return 0
            
            # Sort dates in descending order (newest first)
            distinct_dates.sort(reverse=True)
            
            # Calculate streak from today backwards
            today = date.today()
            streak = 0
            current_date = today
            
            for analysis_date in distinct_dates:
                # Check if this date matches the expected date in the streak
                if analysis_date == current_date or analysis_date == current_date - timedelta(days=1):
                    if analysis_date == current_date:
                        # Same day - continue streak
                        streak += 1
                    else:
                        # Previous day - continue streak
                        streak += 1
                        current_date = analysis_date
                elif analysis_date < current_date - timedelta(days=1):
                    # Gap in streak - break
                    break
                # If analysis_date > current_date, it's in the future, skip
            
            return streak
            
        except Exception as e:
            logger.error(f"Failed to calculate daily streak: {e}", exc_info=True)
            return 0
    
    def get_weekly_summary(self, user_id: int) -> WeeklySummaryResponse:
        """
        Get weekly summary statistics for a user.
        
        Args:
            user_id: The user ID to get summary for
            
        Returns:
            WeeklySummaryResponse with weekly statistics
        """
        try:
            # Calculate current week (Monday to Sunday)
            today = date.today()
            days_since_monday = today.weekday()
            week_start = today - timedelta(days=days_since_monday)
            week_end = week_start + timedelta(days=6)
            
            # Get analyses for current week
            week_analyses = self.repository.get_weekly_analyses(user_id, week_start, week_end)
            
            # Calculate previous week
            prev_week_start = week_start - timedelta(days=7)
            prev_week_end = week_end - timedelta(days=7)
            prev_week_analyses = self.repository.get_weekly_analyses(user_id, prev_week_start, prev_week_end)
            
            # Calculate average skin health for current week
            skin_scores = []
            for analysis in week_analyses:
                if analysis.analysis_data:
                    skin_data = analysis.analysis_data.get("skin") or analysis.analysis_data.get("features", {}).get("skin")
                    if skin_data and isinstance(skin_data, dict):
                        ita_score = skin_data.get("ita_score")
                        if ita_score is not None:
                            normalized = ((float(ita_score) + 50) / 110) * 100
                            skin_scores.append(max(0, min(100, normalized)))
            
            average_skin_health = sum(skin_scores) / len(skin_scores) if skin_scores else None
            
            # Calculate improvement percentage
            improvement_percentage = None
            if prev_week_analyses and week_analyses:
                prev_skin_scores = []
                for analysis in prev_week_analyses:
                    if analysis.analysis_data:
                        skin_data = analysis.analysis_data.get("skin") or analysis.analysis_data.get("features", {}).get("skin")
                        if skin_data and isinstance(skin_data, dict):
                            ita_score = skin_data.get("ita_score")
                            if ita_score is not None:
                                normalized = ((float(ita_score) + 50) / 110) * 100
                                prev_skin_scores.append(max(0, min(100, normalized)))
                
                if prev_skin_scores and skin_scores:
                    prev_avg = sum(prev_skin_scores) / len(prev_skin_scores)
                    curr_avg = sum(skin_scores) / len(skin_scores)
                    if prev_avg > 0:
                        improvement_percentage = ((curr_avg - prev_avg) / prev_avg) * 100
            
            return WeeklySummaryResponse(
                analyses_count=len(week_analyses),
                average_skin_health=average_skin_health,
                improvement_percentage=improvement_percentage,
                week_start_date=datetime.combine(week_start, datetime.min.time()),
                week_end_date=datetime.combine(week_end, datetime.max.time())
            )
            
        except Exception as e:
            logger.error(f"Failed to get weekly summary: {e}", exc_info=True)
            today = date.today()
            days_since_monday = today.weekday()
            week_start = today - timedelta(days=days_since_monday)
            week_end = week_start + timedelta(days=6)
            
            return WeeklySummaryResponse(
                analyses_count=0,
                average_skin_health=None,
                improvement_percentage=None,
                week_start_date=datetime.combine(week_start, datetime.min.time()),
                week_end_date=datetime.combine(week_end, datetime.max.time())
            )
    
    def get_achievements(self, user_id: int) -> AchievementsResponse:
        """
        Get user achievements based on grooming history.
        
        Args:
            user_id: The user ID to get achievements for
            
        Returns:
            AchievementsResponse with unlocked badges
        """
        try:
            total_count = self.repository.count_by_user_id(user_id)
            daily_streak = self._calculate_daily_streak(user_id)
            latest = self.repository.get_latest_by_user_id(user_id)
            
            badges = []
            
            # First Analysis Complete
            first_analysis_unlocked = total_count >= 1
            badges.append(AchievementBadge(
                id="first_analysis",
                title="First Analysis Complete",
                description="Complete your first grooming analysis",
                icon="check_circle",
                unlocked=first_analysis_unlocked,
                unlocked_at=latest.created_at if first_analysis_unlocked and latest else None
            ))
            
            # 7 Day Streak
            streak_7_unlocked = daily_streak >= 7
            badges.append(AchievementBadge(
                id="streak_7",
                title="7 Day Streak",
                description="Maintain a 7-day analysis streak",
                icon="local_fire_department",
                unlocked=streak_7_unlocked,
                unlocked_at=latest.created_at if streak_7_unlocked and latest else None
            ))
            
            # 10 Analyses Done
            analyses_10_unlocked = total_count >= 10
            badges.append(AchievementBadge(
                id="analyses_10",
                title="10 Analyses Done",
                description="Complete 10 grooming analyses",
                icon="star",
                unlocked=analyses_10_unlocked,
                unlocked_at=latest.created_at if analyses_10_unlocked and latest else None
            ))
            
            total_unlocked = sum(1 for badge in badges if badge.unlocked)
            
            return AchievementsResponse(
                badges=badges,
                total_unlocked=total_unlocked
            )
            
        except Exception as e:
            logger.error(f"Failed to get achievements: {e}", exc_info=True)
            return AchievementsResponse(
                badges=[],
                total_unlocked=0
            )

