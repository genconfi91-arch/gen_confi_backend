"""
API v1 router configuration.
"""
from fastapi import APIRouter
from app.api.v1.endpoints import users, auth, analysis
from app.core.config import settings

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)

api_router.include_router(
    analysis.router,
    prefix="/analysis",
    tags=["analysis"]
)

