"""
Analysis API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from app.api.deps import get_database, get_current_user
from app.services.analysis_service import AnalysisService
from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.schemas.user import UserResponse

router = APIRouter()


@router.post(
    "/complete-analysis",
    response_model=AnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit complete analysis",
    description="Submit user image, chat answers, and gender for analysis with groomify_ml integration",
    tags=["analysis"]
)
async def complete_analysis(
    image: UploadFile = File(..., description="User image file"),
    answers: str = Form(..., description="Chat answers as JSON string"),
    gender: str = Form(..., description="User gender: 'male' or 'female' (required for groomify_ml analysis)"),
    metadata: str = Form(default="{}", description="Additional metadata as JSON string"),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_database)
) -> AnalysisResponse:
    """
    Submit complete analysis with image, chat answers, and gender.
    
    This endpoint integrates with the groomify_ml microservice to provide
    AI-powered facial analysis and styling recommendations.
    
    Args:
        image: Uploaded image file
        answers: Chat answers as JSON string
        gender: User gender ("male" or "female") - required for groomify_ml
        metadata: Additional metadata as JSON string (optional)
        current_user: Current authenticated user
        db: Database session dependency
        
    Returns:
        AnalysisResponse with analysis ID and results from groomify_ml
        
    Raises:
        HTTPException: If validation fails or creation fails
    """
    try:
        # Parse JSON strings
        answers_dict = json.loads(answers)
        metadata_dict = json.loads(metadata) if metadata else {}
        
        # Create AnalysisRequest object
        analysis_request = AnalysisRequest(
            answers=answers_dict,
            metadata=metadata_dict
        )
        
        # Create analysis with groomify_ml integration
        service = AnalysisService(db)
        return await service.create_analysis(
            user_id=current_user.id,
            image_file=image,
            analysis_data=analysis_request,
            gender=gender
        )
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON format: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process analysis: {str(e)}"
        )


@router.get(
    "/{analysis_id}",
    response_model=AnalysisResponse,
    summary="Get analysis by ID",
    description="Retrieve a specific analysis by its ID",
    tags=["analysis"]
)
def get_analysis(
    analysis_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_database)
) -> AnalysisResponse:
    """
    Get analysis by ID.
    
    Args:
        analysis_id: Analysis ID
        current_user: Current authenticated user
        db: Database session dependency
        
    Returns:
        AnalysisResponse object
        
    Raises:
        HTTPException: If analysis not found or access denied
    """
    service = AnalysisService(db)
    return service.get_analysis(analysis_id, current_user.id)


@router.get(
    "/",
    response_model=List[AnalysisResponse],
    summary="Get user analyses",
    description="Get all analyses for the current user",
    tags=["analysis"]
)
def get_user_analyses(
    skip: int = 0,
    limit: int = 10,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_database)
) -> List[AnalysisResponse]:
    """
    Get all analyses for current user.
    
    Args:
        skip: Number of results to skip
        limit: Maximum number of results
        current_user: Current authenticated user
        db: Database session dependency
        
    Returns:
        List of AnalysisResponse objects
    """
    service = AnalysisService(db)
    return service.get_user_analyses(current_user.id, limit=limit, skip=skip)

