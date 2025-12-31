"""
User repository for database operations.
Implements repository pattern for data access layer.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.logging import get_logger

logger = get_logger(__name__)


class UserRepository:
    """Repository for user database operations."""
    
    def __init__(self, db: Session):
        """
        Initialize repository with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: The user ID to search for
            
        Returns:
            User object if found, None otherwise
        """
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            email: The email address to search for
            
        Returns:
            User object if found, None otherwise
        """
        return self.db.query(User).filter(User.email == email).first()
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """
        Get all users with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of User objects
        """
        return self.db.query(User).offset(skip).limit(limit).all()
    
    def create(self, user_data: UserCreate, password: Optional[str] = None) -> User:
        """
        Create a new user.
        
        Args:
            user_data: User creation data
            password: Hashed password (required for user creation)
            
        Returns:
            Created User object
            
        Raises:
            IntegrityError: If email already exists
            ValueError: If password is not provided
        """
        if password is None:
            raise ValueError("Password is required to create a user")
        
        user_dict = user_data.model_dump()
        user_dict['password'] = password
        db_user = User(**user_dict)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        logger.info(f"Created user with ID: {db_user.id}, email: {db_user.email}")
        return db_user
    
    def update(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """
        Update an existing user.
        
        Args:
            user_id: The ID of the user to update
            user_data: User update data
            
        Returns:
            Updated User object if found, None otherwise
            
        Raises:
            IntegrityError: If email already exists
        """
        db_user = self.get_by_id(user_id)
        if not db_user:
            return None
        
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        self.db.commit()
        self.db.refresh(db_user)
        logger.info(f"Updated user with ID: {user_id}")
        return db_user
    
    def delete(self, user_id: int) -> bool:
        """
        Delete a user by ID.
        
        Args:
            user_id: The ID of the user to delete
            
        Returns:
            True if user was deleted, False if not found
        """
        db_user = self.get_by_id(user_id)
        if not db_user:
            return False
        
        self.db.delete(db_user)
        self.db.commit()
        logger.info(f"Deleted user with ID: {user_id}")
        return True
    
    def count(self) -> int:
        """
        Get total count of users.
        
        Returns:
            Total number of users
        """
        return self.db.query(User).count()

