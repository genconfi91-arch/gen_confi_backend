"""
Analysis service for business logic.
"""
import os
import uuid
from typing import Dict, Any
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.analysis_repository import AnalysisRepository
from app.schemas.analysis import (
    AnalysisRequest, 
    AnalysisResponse, 
    FaceAnalysisResponse, 
    StyleRecommendationsResponse, 
    PersonalizedInsightsResponse,
    HairstyleRecommendation
)


class AnalysisService:
    """Service for analysis operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = AnalysisRepository(db)
        self.uploads_dir = "uploads/analyses"
        
        # Create uploads directory if it doesn't exist
        os.makedirs(self.uploads_dir, exist_ok=True)
    
    def save_image(self, file: UploadFile, user_id: int) -> str:
        """
        Save uploaded image to disk.
        
        Args:
            file: Uploaded file object
            user_id: User ID for organizing files
            
        Returns:
            Relative path to saved image
            
        Raises:
            HTTPException: If file is invalid or save fails
        """
        # Validate file type
        allowed_extensions = {".jpg", ".jpeg", ".png", ".heic"}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Generate unique filename
        unique_id = str(uuid.uuid4())[:8]
        filename = f"user_{user_id}_analysis_{unique_id}{file_ext}"
        file_path = os.path.join(self.uploads_dir, filename)
        
        # Save file
        try:
            with open(file_path, "wb") as buffer:
                content = file.file.read()
                buffer.write(content)
            
            # Return relative path for database storage
            return f"analyses/{filename}"
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save image: {str(e)}"
            )
    
    def create_analysis(
        self, 
        user_id: int, 
        image_file: UploadFile, 
        analysis_data: AnalysisRequest
    ) -> AnalysisResponse:
        """
        Create a complete analysis.
        
        Args:
            user_id: User ID
            image_file: Uploaded image file
            analysis_data: Analysis request data with chat answers
            
        Returns:
            AnalysisResponse object
            
        Raises:
            HTTPException: If creation fails
        """
        try:
            # Save image
            image_path = self.save_image(image_file, user_id)
            
            # Convert chat answers to dict
            chat_answers_dict = analysis_data.answers.model_dump(exclude_none=True)
            
            # Create analysis record
            analysis = self.repository.create(
                user_id=user_id,
                image_path=image_path,
                chat_answers=chat_answers_dict
            )
            
            # Build image URL
            image_url = f"/api/v1/uploads/{image_path}"
            
            # Return response with placeholder data for model integration
            # TODO: Replace with actual model results when model integration is complete
            return AnalysisResponse(
                id=analysis.id,
                user_id=analysis.user_id,
                image_url=image_url,
                chat_answers=analysis.chat_answers,
                face_analysis=FaceAnalysisResponse(
                    status="pending",
                    skin_quality=None,  # Will be populated by model
                    face_matrix=None,  # Will be populated by model
                ),
                style_recommendations=StyleRecommendationsResponse(
                    status="pending",
                    best_hairstyles=[],  # Will contain top 3 hairstyles from model
                ),
                personalized_insights=PersonalizedInsightsResponse(status="pending"),
                created_at=analysis.created_at,
                updated_at=analysis.updated_at
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create analysis: {str(e)}"
            )
    
    def get_analysis(self, analysis_id: int, user_id: int) -> AnalysisResponse:
        """
        Get analysis by ID (with user verification).
        
        Args:
            analysis_id: Analysis ID
            user_id: User ID (to verify ownership)
            
        Returns:
            AnalysisResponse object
            
        Raises:
            HTTPException: If analysis not found or access denied
        """
        analysis = self.repository.get_by_id(analysis_id)
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found"
            )
        
        if analysis.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Build image URL
        image_url = f"/api/v1/uploads/{analysis.image_path}"
        
        # Convert stored data to response format
        face_analysis_data = analysis.face_analysis or {"status": "pending"}
        face_analysis = FaceAnalysisResponse(
            **face_analysis_data,
            skin_quality=face_analysis_data.get("skin_quality"),
            face_matrix=face_analysis_data.get("face_matrix"),
        )
        
        style_recommendations_data = analysis.style_recommendations or {"status": "pending"}
        # Convert best_hairstyles from dict to HairstyleRecommendation objects if present
        best_hairstyles_list = style_recommendations_data.get("best_hairstyles", [])
        if best_hairstyles_list and isinstance(best_hairstyles_list[0], dict):
            best_hairstyles_list = [HairstyleRecommendation(**item) for item in best_hairstyles_list]
        
        style_recommendations = StyleRecommendationsResponse(
            **style_recommendations_data,
            best_hairstyles=best_hairstyles_list,
        )
        personalized_insights = PersonalizedInsightsResponse(
            **(analysis.personalized_insights or {"status": "pending"})
        )
        
        return AnalysisResponse(
            id=analysis.id,
            user_id=analysis.user_id,
            image_url=image_url,
            chat_answers=analysis.chat_answers,
            face_analysis=face_analysis,
            style_recommendations=style_recommendations,
            personalized_insights=personalized_insights,
            created_at=analysis.created_at,
            updated_at=analysis.updated_at
        )
    
    def get_user_analyses(self, user_id: int, limit: int = 10, skip: int = 0) -> list[AnalysisResponse]:
        """
        Get all analyses for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of results
            skip: Number of results to skip
            
        Returns:
            List of AnalysisResponse objects
        """
        analyses = self.repository.get_by_user_id(user_id, limit=limit, skip=skip)
        
        result = []
        for analysis in analyses:
            face_analysis_data = analysis.face_analysis or {"status": "pending"}
            style_recommendations_data = analysis.style_recommendations or {"status": "pending"}
            
            # Convert best_hairstyles from dict to HairstyleRecommendation objects if present
            best_hairstyles_list = style_recommendations_data.get("best_hairstyles", [])
            if best_hairstyles_list and isinstance(best_hairstyles_list[0], dict):
                best_hairstyles_list = [HairstyleRecommendation(**item) for item in best_hairstyles_list]
            
            result.append(
                AnalysisResponse(
                    id=analysis.id,
                    user_id=analysis.user_id,
                    image_url=f"/api/v1/uploads/{analysis.image_path}",
                    chat_answers=analysis.chat_answers,
                    face_analysis=FaceAnalysisResponse(
                        **face_analysis_data,
                        skin_quality=face_analysis_data.get("skin_quality"),
                        face_matrix=face_analysis_data.get("face_matrix"),
                    ),
                    style_recommendations=StyleRecommendationsResponse(
                        **style_recommendations_data,
                        best_hairstyles=best_hairstyles_list,
                    ),
                    personalized_insights=PersonalizedInsightsResponse(
                        **(analysis.personalized_insights or {"status": "pending"})
                    ),
                    created_at=analysis.created_at,
                    updated_at=analysis.updated_at
                )
            )
        return result

