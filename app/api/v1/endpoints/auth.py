"""
Authentication API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_database, get_current_user
from app.services.auth_service import AuthService
from app.schemas.auth import SignupRequest, LoginRequest, LoginResponse, ForgotPasswordRequest, ResetPasswordRequest
from app.schemas.user import UserResponse

router = APIRouter()


@router.post(
    "/signup",
    response_model=LoginResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email, name, phone, and password",
    tags=["auth"]
)
def signup(
    signup_data: SignupRequest,
    db: Session = Depends(get_database)
) -> LoginResponse:
    """
    Register a new user.
    
    Args:
        signup_data: User signup information
        db: Database session dependency
        
    Returns:
        LoginResponse with access token and user data
        
    Raises:
        HTTPException: If email already exists or validation fails
    """
    service = AuthService(db)
    return service.signup(signup_data)


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login user",
    description="Authenticate user with email and password",
    tags=["auth"]
)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_database)
) -> LoginResponse:
    """
    Authenticate user and return access token.
    
    Args:
        login_data: User login credentials
        db: Database session dependency
        
    Returns:
        LoginResponse with access token and user data
        
    Raises:
        HTTPException: If credentials are invalid
    """
    service = AuthService(db)
    return service.login(login_data)


@router.post(
    "/forgot-password",
    summary="Forgot password",
    description="Request password reset token",
    tags=["auth"]
)
def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_database)
):
    """
    Request password reset.
    
    Args:
        request: ForgotPasswordRequest with email
        db: Database session
    """
    service = AuthService(db)
    return service.forgot_password(request)


@router.post(
    "/reset-password",
    summary="Reset password",
    description="Reset password using token",
    tags=["auth"]
)
def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_database)
):
    """
    Reset password with token.
    
    Args:
        request: ResetPasswordRequest with token and new password
        db: Database session
    """
    service = AuthService(db)
    return service.reset_password(request)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get information about the currently authenticated user",
    tags=["auth"]
)
def get_current_user_info(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """
    Get current authenticated user information.
    
    Args:
        current_user: Current user from JWT token dependency
        
    Returns:
        UserResponse with current user data
    """
    return current_user
