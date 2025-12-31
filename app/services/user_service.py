"""
User service for business logic.
Implements service layer pattern for business operations.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate, UserResponse
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
    
    def get_user_by_id(self, user_id: int) -> UserResponse:
        """
        Get user by ID.
        
        Args:
            user_id: The user ID
            
        Returns:
            UserResponse object
            
        Raises:
            HTTPException: If user not found
        """
        user = self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        return UserResponse.model_validate(user)
    
    def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """
        Get user by email.
        
        Args:
            email: The email address
            
        Returns:
            UserResponse object if found, None otherwise
        """
        user = self.repository.get_by_email(email)
        if user:
            return UserResponse.model_validate(user)
        return None
    
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
    
    def create_user(self, user_data: UserCreate, password: Optional[str] = None) -> UserResponse:
        """
        Create a new user.
        
        Args:
            user_data: User creation data
            password: Optional password (if not provided, a temporary password will be generated)
            
        Returns:
            Created UserResponse object
            
        Raises:
            HTTPException: If email already exists
        """
        # Check if user with email already exists
        existing_user = self.repository.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with email {user_data.email} already exists"
            )
        
        try:
            from app.core.security import get_password_hash
            
            # Hash password (use provided password or generate temporary one)
            if password:
                hashed_password = get_password_hash(password)
            else:
                # Generate a temporary password that user must change
                import secrets
                temp_password = secrets.token_urlsafe(16)
                hashed_password = get_password_hash(temp_password)
                logger.warning(f"Created user {user_data.email} with temporary password")
            
            # Create user using repository
            user = self.repository.create(user_data, password=hashed_password)
            return UserResponse.model_validate(user)
        except IntegrityError as e:
            logger.error(f"Integrity error creating user: {e}")
            self.repository.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with email {user_data.email} already exists"
            ) from e
    
    def update_user(
        self,
        user_id: int,
        user_data: UserUpdate
    ) -> UserResponse:
        """
        Update an existing user.
        
        Args:
            user_id: The ID of the user to update
            user_data: User update data
            
        Returns:
            Updated UserResponse object
            
        Raises:
            HTTPException: If user not found or email already exists
        """
        # Check if email is being updated and if it already exists
        if user_data.email:
            existing_user = self.repository.get_by_email(user_data.email)
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User with email {user_data.email} already exists"
                )
        
        try:
            user = self.repository.update(user_id, user_data)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with ID {user_id} not found"
                )
            return UserResponse.model_validate(user)
        except IntegrityError as e:
            logger.error(f"Integrity error updating user: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
    
    def delete_user(self, user_id: int) -> None:
        """
        Delete a user by ID.
        
        Args:
            user_id: The ID of the user to delete
            
        Raises:
            HTTPException: If user not found
        """
        deleted = self.repository.delete(user_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
    
    def get_user_count(self) -> int:
        """
        Get total count of users.
        
        Returns:
            Total number of users
        """
        return self.repository.count()

