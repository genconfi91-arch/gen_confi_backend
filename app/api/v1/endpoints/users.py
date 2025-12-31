"""
User API endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.deps import get_database
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.utils.pagination import PaginationParams, pagination_params

router = APIRouter()


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Create a new user with email and name",
    tags=["users"]
)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_database)
) -> UserResponse:
    """
    Create a new user.
    
    Args:
        user_data: User creation data
        db: Database session dependency
        
    Returns:
        Created user response
    """
    service = UserService(db)
    return service.create_user(user_data)


@router.get(
    "/",
    response_model=List[UserResponse],
    summary="Get all users",
    description="Get a list of all users with pagination",
    tags=["users"]
)
def get_users(
    pagination: PaginationParams = Depends(pagination_params),
    db: Session = Depends(get_database)
) -> List[UserResponse]:
    """
    Get all users with pagination.
    
    Args:
        pagination: Pagination parameters
        db: Database session dependency
        
    Returns:
        List of user responses
    """
    service = UserService(db)
    return service.get_users(skip=pagination.skip, limit=pagination.limit)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Get a specific user by their ID",
    tags=["users"]
)
def get_user(
    user_id: int,
    db: Session = Depends(get_database)
) -> UserResponse:
    """
    Get user by ID.
    
    Args:
        user_id: The user ID
        db: Database session dependency
        
    Returns:
        User response
    """
    service = UserService(db)
    return service.get_user_by_id(user_id)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user",
    description="Update an existing user's information",
    tags=["users"]
)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_database)
) -> UserResponse:
    """
    Update user by ID.
    
    Args:
        user_id: The user ID
        user_data: User update data
        db: Database session dependency
        
    Returns:
        Updated user response
    """
    service = UserService(db)
    return service.update_user(user_id, user_data)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Delete a user by their ID",
    tags=["users"]
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_database)
) -> None:
    """
    Delete user by ID.
    
    Args:
        user_id: The user ID
        db: Database session dependency
    """
    service = UserService(db)
    service.delete_user(user_id)

