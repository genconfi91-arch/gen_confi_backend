"""
Authentication service for business logic.
Handles user signup, login, and token management.
"""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.repositories.user_repository import UserRepository
from app.schemas.auth import SignupRequest, LoginRequest, LoginResponse, ForgotPasswordRequest, ResetPasswordRequest, ChangePasswordRequest
from app.schemas.user import UserResponse
from app.models.user import User, UserRole
from app.core.security import get_password_hash, verify_password, create_access_token, decode_access_token
from app.core.config import settings
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
            
            # Create user with hashed password using repository
            from app.schemas.user import UserCreate
            user_data = UserCreate(
                email=signup_data.email,
                name=signup_data.name,
                phone=signup_data.phone,
                gender=signup_data.gender,
                role=UserRole.CLIENT  # Default role for new signups
            )
            
            # Create user in database using repository
            db_user = self.repository.create(user_data, password=hashed_password)
            
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
            logger.error(f"Error during signup: {e}", exc_info=True)
            self.repository.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred during signup: {str(e)}"
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
        # Hardcoded Admin Check
        if login_data.email == settings.ADMIN_EMAIL and login_data.password == settings.ADMIN_PASSWORD:
            logger.info("Admin logged in via hardcoded credentials")
            admin_user = User(
                id=0,
                email=settings.ADMIN_EMAIL,
                name="System Admin",
                role=UserRole.ADMIN,
                phone="0000000000"
            )
            access_token = self._create_user_token(admin_user)
            return LoginResponse(
                access_token=access_token,
                token_type="bearer",
                user=UserResponse(
                    id=0,
                    email=settings.ADMIN_EMAIL,
                    name="System Admin",
                    role=UserRole.ADMIN,
                    phone="0000000000"
                )
            )

        try:
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
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"CRITICAL LOGIN ERROR: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error during login: {str(e)}"
            )

    def forgot_password(self, request: ForgotPasswordRequest):
        """
        Initiate password reset flow.
        
        Args:
            request: ForgotPasswordRequest with email
            
        Returns:
            Message indicating status
        """
        user = self.repository.get_by_email(request.email)
        if not user:
            # For security, we respond with success even if email not found
            # But we'll log it for debugging
            logger.warning(f"Forgot password requested for non-existent email: {request.email}")
            return {"message": "If this email is registered, you will receive password reset instructions."}

        # Generate reset token (short lived, e.g., 15 mins)
        from datetime import timedelta
        reset_token = create_access_token(
            data={"sub": str(user.id), "type": "reset"},
            expires_delta=timedelta(minutes=15)
        )
        
        # In a real app, send this via email.
        # Here we just log it for the developer/demo usage.
        logger.info(f"PASSWORD RESET TOKEN for {user.email}: {reset_token}")
        
        # We can return the token in development mode only
        if settings.DEBUG:
            return {
                "message": "Password reset token generated (DEBUG MODE)",
                "reset_token": reset_token
            }
            
        return {"message": "If this email is registered, you will receive password reset instructions."}

    def reset_password(self, request: ResetPasswordRequest):
        """
        Reset user password using token.
        
        Args:
            request: ResetPasswordRequest with token and new password
            
        Returns:
            Success message
        """
        payload = decode_access_token(request.token)
        if not payload or payload.get("type") != "reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
            
        user_id = int(payload.get("sub"))
        user = self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        # Update password
        hashed_password = get_password_hash(request.new_password)
        
        # Manually update password since we don't have update_user service method anymore
        user.password = hashed_password
        self.repository.db.commit()
        self.repository.db.refresh(user)
        
        logger.info(f"Password reset successful for user: {user.email}")
        return {"message": "Password has been reset successfully"}
    
    def change_password(self, user_id: int, request: ChangePasswordRequest):
        """
        Change user password (requires current password).
        
        Args:
            user_id: ID of the user changing password
            request: ChangePasswordRequest with current and new password
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If current password is incorrect or user not found
        """
        user = self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        if not verify_password(request.current_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        hashed_password = get_password_hash(request.new_password)
        user.password = hashed_password
        self.repository.db.commit()
        self.repository.db.refresh(user)
        
        logger.info(f"Password changed successfully for user: {user.email}")
        return {"message": "Password has been changed successfully"}
    
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
