"""
Pagination utilities for API endpoints.
"""
from typing import Optional
from fastapi import Query
from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    """Pagination parameters model."""
    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum number of records to return")


def pagination_params(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum number of records to return")
) -> PaginationParams:
    """
    Dependency function for pagination parameters.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        PaginationParams object
    """
    return PaginationParams(skip=skip, limit=limit)

