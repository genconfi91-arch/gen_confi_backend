"""
User service for business logic.
Implements service layer pattern for business operations.
"""
from typing import List
from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserResponse, UserUpdate
from app.core.logging import get_logger

logger = get_logger(__name__)


class UserService:
    """Service for user business logic."""
    
    def __init__(self, db: Session):
        """
        Initialize service with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.repository = UserRepository(db)
    
    def get_users(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserResponse]:
        """
        Get all users with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of UserResponse objects
        """
        users = self.repository.get_all(skip=skip, limit=limit)
        return [UserResponse.model_validate(user) for user in users]

    def update_user(self, user_id: int, user_data: UserUpdate) -> UserResponse:
        """
        Update a user.
        
        Args:
            user_id: ID of the user to update
            user_data: New user data
            
        Returns:
            Updated UserResponse object
            
        Raises:
            ValueError: If user not found
        """
        user = self.repository.update(user_id, user_data)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        return UserResponse.model_validate(user)
