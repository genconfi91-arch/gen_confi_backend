"""
GroomingHistory repository for database operations.
Implements repository pattern for data access layer.
"""
from typing import Optional, List
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, func, distinct
from sqlalchemy.sql import text
from app.models.grooming_history import GroomingHistory
from app.schemas.grooming_history import GroomingHistoryCreate, GroomingHistoryUpdate
from app.core.logging import get_logger

logger = get_logger(__name__)


class GroomingHistoryRepository:
    """Repository for grooming history database operations."""
    
    def __init__(self, db: Session):
        """
        Initialize repository with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def create(
        self,
        user_id: int,
        grooming_data: GroomingHistoryCreate
    ) -> GroomingHistory:
        """
        Create a new grooming history record.
        
        Args:
            user_id: The user ID who owns this grooming history
            grooming_data: Grooming history creation data
            
        Returns:
            Created GroomingHistory object
        """
        db_grooming = GroomingHistory(
            user_id=user_id,
            analysis_data=grooming_data.analysis_data,
            before_image_url=grooming_data.before_image_url,
            after_image_url=grooming_data.after_image_url,
            status=grooming_data.status
        )
        self.db.add(db_grooming)
        self.db.commit()
        self.db.refresh(db_grooming)
        logger.info(f"Created grooming history with ID: {db_grooming.id} for user: {user_id}")
        return db_grooming
    
    def get_by_id(self, grooming_id: int) -> Optional[GroomingHistory]:
        """
        Get grooming history by ID.
        
        Args:
            grooming_id: The grooming history ID to search for
            
        Returns:
            GroomingHistory object if found, None otherwise
        """
        return self.db.query(GroomingHistory).filter(GroomingHistory.id == grooming_id).first()
    
    def get_by_user_id(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
        order_by: str = "created_at",
        order: str = "desc"
    ) -> List[GroomingHistory]:
        """
        Get all grooming history for a specific user with pagination and sorting.
        
        Args:
            user_id: The user ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Field to sort by (default: "created_at")
            order: Sort direction "asc" or "desc" (default: "desc")
            
        Returns:
            List of GroomingHistory objects
        """
        query = self.db.query(GroomingHistory).filter(GroomingHistory.user_id == user_id)
        
        # Apply sorting
        if hasattr(GroomingHistory, order_by):
            sort_field = getattr(GroomingHistory, order_by)
            if order.lower() == "desc":
                query = query.order_by(desc(sort_field))
            else:
                query = query.order_by(asc(sort_field))
        else:
            # Default to created_at desc if invalid field
            query = query.order_by(desc(GroomingHistory.created_at))
        
        # Apply pagination
        return query.offset(skip).limit(limit).all()
    
    def count_by_user_id(self, user_id: int) -> int:
        """
        Get total count of grooming history records for a user.
        
        Args:
            user_id: The user ID to count for
            
        Returns:
            Total number of grooming history records
        """
        return self.db.query(GroomingHistory).filter(GroomingHistory.user_id == user_id).count()
    
    def update(
        self,
        grooming_id: int,
        grooming_data: GroomingHistoryUpdate
    ) -> Optional[GroomingHistory]:
        """
        Update an existing grooming history record.
        
        Args:
            grooming_id: The ID of the grooming history to update
            grooming_data: Grooming history update data
            
        Returns:
            Updated GroomingHistory object if found, None otherwise
        """
        db_grooming = self.get_by_id(grooming_id)
        if not db_grooming:
            return None
        
        update_data = grooming_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_grooming, field, value)
        
        self.db.commit()
        self.db.refresh(db_grooming)
        logger.info(f"Updated grooming history with ID: {grooming_id}")
        return db_grooming
    
    def delete(self, grooming_id: int) -> bool:
        """
        Delete a grooming history record by ID.
        
        Args:
            grooming_id: The ID of the grooming history to delete
            
        Returns:
            True if grooming history was deleted, False if not found
        """
        db_grooming = self.get_by_id(grooming_id)
        if not db_grooming:
            return False
        
        self.db.delete(db_grooming)
        self.db.commit()
        logger.info(f"Deleted grooming history with ID: {grooming_id}")
        return True
    
    def get_all_by_user_id(self, user_id: int) -> List[GroomingHistory]:
        """
        Get all grooming history for a user (no pagination).
        
        Args:
            user_id: The user ID to filter by
            
        Returns:
            List of all GroomingHistory objects for the user
        """
        return self.db.query(GroomingHistory).filter(
            GroomingHistory.user_id == user_id
        ).order_by(desc(GroomingHistory.created_at)).all()
    
    def get_latest_by_user_id(self, user_id: int) -> Optional[GroomingHistory]:
        """
        Get the latest grooming history for a user.
        
        Args:
            user_id: The user ID to filter by
            
        Returns:
            Latest GroomingHistory object or None
        """
        return self.db.query(GroomingHistory).filter(
            GroomingHistory.user_id == user_id
        ).order_by(desc(GroomingHistory.created_at)).first()
    
    def get_previous_by_user_id(self, user_id: int) -> Optional[GroomingHistory]:
        """
        Get the second latest grooming history for a user.
        
        Args:
            user_id: The user ID to filter by
            
        Returns:
            Second latest GroomingHistory object or None
        """
        return self.db.query(GroomingHistory).filter(
            GroomingHistory.user_id == user_id
        ).order_by(desc(GroomingHistory.created_at)).offset(1).first()
    
    def get_weekly_analyses(self, user_id: int, week_start: date, week_end: date) -> List[GroomingHistory]:
        """
        Get all grooming history for a user within a date range.
        
        Args:
            user_id: The user ID to filter by
            week_start: Start date of the week
            week_end: End date of the week
            
        Returns:
            List of GroomingHistory objects in the date range
        """
        return self.db.query(GroomingHistory).filter(
            GroomingHistory.user_id == user_id,
            func.date(GroomingHistory.created_at) >= week_start,
            func.date(GroomingHistory.created_at) <= week_end
        ).order_by(desc(GroomingHistory.created_at)).all()
    
    def get_distinct_dates_by_user_id(self, user_id: int) -> List[date]:
        """
        Get distinct dates when user has grooming history entries.
        
        Args:
            user_id: The user ID to filter by
            
        Returns:
            List of distinct dates (date objects)
        """
        results = self.db.query(
            func.date(GroomingHistory.created_at).label('analysis_date')
        ).filter(
            GroomingHistory.user_id == user_id
        ).distinct().order_by(desc('analysis_date')).all()
        
        return [row[0] for row in results if row[0] is not None]

