import shutil
import os
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from app.api.deps import get_database, get_current_user
from app.services.user_service import UserService
from app.schemas.user import UserResponse, UserUpdate, AvatarUpdate
from app.models.user import UserRole
from app.utils.pagination import PaginationParams, pagination_params

router = APIRouter()


@router.get(
    "/",
    response_model=List[UserResponse],
    summary="Get all users",
    description="Get a list of all users with pagination (Admin only)",
    tags=["users"],
    dependencies=[Depends(get_current_user)]
)
def get_users(
    pagination: PaginationParams = Depends(pagination_params),
    db: Session = Depends(get_database),
    current_user: UserResponse = Depends(get_current_user)
) -> List[UserResponse]:
    """
    Get all users with pagination.
    Only accessible by Admin.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )
        
    service = UserService(db)
    return service.get_users(skip=pagination.skip, limit=pagination.limit)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get the details of the currently authenticated user",
    tags=["users"],
    dependencies=[Depends(get_current_user)]
)
def get_me(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """Get current authenticated user."""
    return current_user


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update current user",
    description="Update the profile details of the currently authenticated user",
    tags=["users"],
    dependencies=[Depends(get_current_user)]
)
def update_me(
    user_data: UserUpdate,
    db: Session = Depends(get_database),
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """Update current authenticated user."""
    service = UserService(db)
    try:
        updated_user = service.update_user(current_user.id, user_data)
        return updated_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post(
    "/me/avatar",
    response_model=UserResponse,
    summary="Upload avatar",
    description="Upload a profile photo for the current user",
    tags=["users"]
)
async def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_database),
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """Upload profile photo for current user."""
    import time
    
    # Ensure directory exists
    os.makedirs("uploads/avatars", exist_ok=True)
    
    # Generate unique file name to avoid caching issues
    file_ext = file.filename.split(".")[-1]
    timestamp = int(time.time())
    file_name = f"user_{current_user.id}_avatar_{timestamp}.{file_ext}"
    file_path = f"uploads/avatars/{file_name}"
    
    # Delete old avatar if it exists and is local
    if current_user.avatar_url and not current_user.avatar_url.startswith('http'):
        if os.path.exists(current_user.avatar_url):
            try:
                os.remove(current_user.avatar_url)
            except Exception as e:
                print(f"Error deleting old avatar: {e}")
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update user in DB with local path (relative to mount)
    avatar_url = f"uploads/avatars/{file_name}"
    
    service = UserService(db)
    return service.update_user(current_user.id, UserUpdate(avatar_url=avatar_url))
