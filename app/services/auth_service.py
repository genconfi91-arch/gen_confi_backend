"""
Authentication service for business logic.
Handles user signup, login, and token management.
"""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.repositories.user_repository import UserRepository
from app.schemas.auth import SignupRequest, LoginRequest, LoginResponse
from app.schemas.user import UserResponse
from app.models.user import User, UserRole
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.logging import get_logger

logger = get_logger(__name__)


class AuthService:
    """Service for authentication business logic."""
    
    def __init__(self, db: Session):
        """
        Initialize service with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.repository = UserRepository(db)
    
    def signup(self, signup_data: SignupRequest) -> LoginResponse:
        """
        Register a new user.
        
        Args:
            signup_data: User signup data (name, email, phone, password)
            
        Returns:
            LoginResponse with access token and user data
            
        Raises:
            HTTPException: If email already exists or validation fails
        """
        # Check if user with email already exists
        existing_user = self.repository.get_by_email(signup_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        try:
            # Hash password
            hashed_password = get_password_hash(signup_data.password)
            
            # Create user with hashed password
            from app.schemas.user import UserCreate
            user_data = UserCreate(
                email=signup_data.email,
                name=signup_data.name,
                phone=signup_data.phone,
                role=UserRole.CLIENT  # Default role for new signups
            )
            
            # Create user in database with password
            db_user = User(
                email=user_data.email,
                name=user_data.name,
                phone=user_data.phone,
                password=hashed_password,
                role=user_data.role
            )
            
            self.repository.db.add(db_user)
            self.repository.db.commit()
            self.repository.db.refresh(db_user)
            
            logger.info(f"User signed up: {db_user.email} (ID: {db_user.id})")
            
            # Generate JWT token
            access_token = self._create_user_token(db_user)
            
            # Return token and user data
            return LoginResponse(
                access_token=access_token,
                token_type="bearer",
                user=UserResponse.model_validate(db_user)
            )
            
        except IntegrityError as e:
            logger.error(f"Integrity error during signup: {e}")
            self.repository.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        except Exception as e:
            logger.error(f"Error during signup: {e}")
            self.repository.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred during signup"
            )
    
    def login(self, login_data: LoginRequest) -> LoginResponse:
        """
        Authenticate user and return access token.
        
        Args:
            login_data: User login data (email, password)
            
        Returns:
            LoginResponse with access token and user data
            
        Raises:
            HTTPException: If credentials are invalid
        """
        # Find user by email
        user = self.repository.get_by_email(login_data.email)
        if not user:
            # Don't reveal if email exists or not (security best practice)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(login_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        logger.info(f"User logged in: {user.email} (ID: {user.id})")
        
        # Generate JWT token
        access_token = self._create_user_token(user)
        
        # Return token and user data
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(user)
        )
    
    def _create_user_token(self, user: User) -> str:
        """
        Create JWT access token for user.
        
        Args:
            user: User object
            
        Returns:
            JWT access token string
        """
        token_data = {
            "sub": str(user.id),  # Subject (user ID)
            "email": user.email,
            "role": user.role.value
        }
        return create_access_token(data=token_data)
    
    def get_user_by_id(self, user_id: int) -> Optional[UserResponse]:
        """
        Get user by ID.
        
        Args:
            user_id: The user ID
            
        Returns:
            UserResponse if found, None otherwise
        """
        user = self.repository.get_by_id(user_id)
        if user:
            return UserResponse.model_validate(user)
        return None

