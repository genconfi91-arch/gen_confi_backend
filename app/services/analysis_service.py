"""
Analysis service for business logic.
"""
import os
import uuid
import base64
import logging
from typing import Dict, Any, Optional
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.analysis_repository import AnalysisRepository
from app.services.groomify_ml_client import GroomifyMLClient
from app.schemas.analysis import (
    AnalysisRequest, 
    AnalysisResponse, 
    FaceAnalysisResponse, 
    StyleRecommendationsResponse, 
    PersonalizedInsightsResponse,
    HairstyleRecommendation
)

logger = logging.getLogger(__name__)


class AnalysisService:
    """Service for analysis operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = AnalysisRepository(db)
        self.uploads_dir = "uploads/analyses"
        self.after_images_dir = "uploads/analyses/after"
        self.groomify_ml_client = GroomifyMLClient()
        
        # Create uploads directories if they don't exist
        os.makedirs(self.uploads_dir, exist_ok=True)
        os.makedirs(self.after_images_dir, exist_ok=True)
    
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
    
    def save_base64_image(self, base64_string: str, user_id: int, analysis_id: int, prefix: str = "after") -> Optional[str]:
        """
        Save base64-encoded image to disk.
        
        Args:
            base64_string: Base64-encoded image string (with or without data URL prefix)
            user_id: User ID for organizing files
            analysis_id: Analysis ID for filename
            prefix: Filename prefix (e.g., "after", "before")
            
        Returns:
            Relative path to saved image, or None if save fails
        """
        try:
            # Remove data URL prefix if present (e.g., "data:image/png;base64,")
            if "," in base64_string:
                base64_string = base64_string.split(",", 1)[1]
            
            # Decode base64
            image_data = base64.b64decode(base64_string)
            
            # Determine file extension from image data
            # Try to detect format from magic bytes
            if image_data.startswith(b'\xff\xd8\xff'):
                ext = ".jpg"
            elif image_data.startswith(b'\x89PNG'):
                ext = ".png"
            else:
                ext = ".png"  # Default to PNG
            
            # Generate filename
            filename = f"user_{user_id}_analysis_{analysis_id}_{prefix}{ext}"
            file_path = os.path.join(self.after_images_dir, filename)
            
            # Save file
            with open(file_path, "wb") as buffer:
                buffer.write(image_data)
            
            # Return relative path
            return f"analyses/after/{filename}"
            
        except Exception as e:
            logger.error(f"Failed to save base64 image: {e}")
            return None
    
    def _map_groomify_ml_response(
        self,
        groomify_response: Dict[str, Any]
    ) -> tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
        """
        Map groomify_ml response to Gen_Confi_Backend schema format.
        
        Args:
            groomify_response: Response from groomify_ml API
            
        Returns:
            Tuple of (face_analysis_dict, style_recommendations_dict, personalized_insights_dict)
        """
        features = groomify_response.get("features", {})
        metrics = features.get("metrics", {})
        skin = groomify_response.get("skin", {})
        recommendations = groomify_response.get("recommendations", {})
        
        # Map face analysis
        face_analysis_dict = {
            "face_shape": groomify_response.get("face_shape"),
            "skin_tone": skin.get("tone"),
            "skin_quality": None,  # Not provided by groomify_ml
            "face_matrix": {
                "face_length": metrics.get("face_length"),
                "face_width": metrics.get("face_width"),
                "forehead_width": metrics.get("forehead_width"),
                "jaw_width": metrics.get("jaw_width"),
                "chin_length": metrics.get("chin_length"),
            },
            "face_metrics": {
                "symmetry_score": None,  # Not provided by groomify_ml
            },
            "status": "completed" if groomify_response.get("status") == "success" else "failed"
        }
        
        # Map style recommendations
        hairstyle_recommendations = recommendations.get("hairstyle_recommendations", [])
        best_hairstyles = []
        for idx, rec in enumerate(hairstyle_recommendations[:3], 1):  # Top 3
            if isinstance(rec, dict):
                best_hairstyles.append({
                    "id": idx,
                    "name": rec.get("name", f"Style {idx}"),
                    "image_url": rec.get("image_url", ""),
                    "description": rec.get("description"),
                    "confidence_score": rec.get("confidence_score"),
                    "suitability_reason": rec.get("suitability_reason")
                })
        
        style_recommendations_dict = {
            "best_hairstyles": best_hairstyles,
            "hairstyles": [],
            "products": [],
            "routines": [],
            "status": "completed" if groomify_response.get("status") == "success" else "failed"
        }
        
        # Map personalized insights
        personalized_insights_dict = {
            "best_styles": recommendations.get("best_styles", []),
            "avoid_styles": recommendations.get("avoid_styles", []),
            "tips": recommendations.get("notes", []),
            "status": "completed" if groomify_response.get("status") == "success" else "failed"
        }
        
        return face_analysis_dict, style_recommendations_dict, personalized_insights_dict
    
    async def create_analysis(
        self, 
        user_id: int, 
        image_file: UploadFile, 
        analysis_data: AnalysisRequest,
        gender: Optional[str] = None
    ) -> AnalysisResponse:
        """
        Create a complete analysis with groomify_ml integration.
        
        Args:
            user_id: User ID
            image_file: Uploaded image file
            analysis_data: Analysis request data with chat answers
            gender: User gender ("male" or "female") - required for groomify_ml
            
        Returns:
            AnalysisResponse object
            
        Raises:
            HTTPException: If creation fails
        """
        try:
            # Validate gender
            if not gender:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Gender is required for analysis"
                )
            
            gender_lower = gender.lower()
            if gender_lower not in ["male", "female"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid gender '{gender}'. Must be 'male' or 'female'."
                )
            
            # Save image
            image_path = self.save_image(image_file, user_id)
            
            # Convert chat answers to dict
            chat_answers_dict = analysis_data.answers.model_dump(exclude_none=True)
            
            # Create analysis record with pending status
            analysis = self.repository.create(
                user_id=user_id,
                image_path=image_path,
                chat_answers=chat_answers_dict
            )
            
            # Build image URL
            image_url = f"/api/v1/uploads/{image_path}"
            
            # Initialize response with placeholder data (will be updated if groomify_ml succeeds)
            face_analysis_dict = {"status": "pending"}
            style_recommendations_dict = {"status": "pending", "best_hairstyles": []}
            personalized_insights_dict = {"status": "pending", "best_styles": [], "avoid_styles": [], "tips": []}
            after_image_path = None
            
            # Call groomify_ml API
            try:
                logger.info(f"Calling groomify_ml API for user {user_id}, analysis {analysis.id}")
                
                # Reset file pointer before sending to groomify_ml
                await image_file.seek(0)
                
                # Call groomify_ml
                groomify_response = await self.groomify_ml_client.analyze_user(
                    image_file=image_file,
                    gender=gender_lower
                )
                
                # Map groomify_ml response to our schema
                face_analysis_dict, style_recommendations_dict, personalized_insights_dict = \
                    self._map_groomify_ml_response(groomify_response)
                
                # Save after_image if provided
                after_image_url = groomify_response.get("after_image_url")
                if after_image_url:
                    after_image_path = self.save_base64_image(
                        after_image_url,
                        user_id,
                        analysis.id,
                        prefix="after"
                    )
                    if after_image_path:
                        logger.info(f"Saved after_image: {after_image_path}")
                
                # Update analysis record with results
                self.repository.update(
                    analysis_id=analysis.id,
                    face_analysis=face_analysis_dict,
                    style_recommendations=style_recommendations_dict,
                    personalized_insights=personalized_insights_dict
                )
                
                logger.info(f"Successfully integrated groomify_ml results for analysis {analysis.id}")
                
            except HTTPException as e:
                # If groomify_ml fails, log error but continue with placeholder data
                logger.error(
                    f"Groomify_ml API call failed for analysis {analysis.id}: {e.detail}. "
                    f"Returning analysis with failed status."
                )
                # Update status to indicate failure
                face_analysis_dict["status"] = "failed"
                style_recommendations_dict["status"] = "failed"
                personalized_insights_dict["status"] = "failed"
                
                # Update database with failed status so subsequent polls return failed
                self.repository.update(
                    analysis_id=analysis.id,
                    face_analysis=face_analysis_dict,
                    style_recommendations=style_recommendations_dict,
                    personalized_insights=personalized_insights_dict
                )
                # Keep placeholder data - analysis is created but not processed
            except Exception as e:
                # Catch any other exceptions (connection errors, timeouts, etc.)
                logger.error(
                    f"Unexpected error calling groomify_ml for analysis {analysis.id}: {str(e)}. "
                    f"Returning analysis with failed status.",
                    exc_info=True
                )
                # Update status to indicate failure
                face_analysis_dict["status"] = "failed"
                style_recommendations_dict["status"] = "failed"
                personalized_insights_dict["status"] = "failed"
                
                # Update database with failed status so subsequent polls return failed
                self.repository.update(
                    analysis_id=analysis.id,
                    face_analysis=face_analysis_dict,
                    style_recommendations=style_recommendations_dict,
                    personalized_insights=personalized_insights_dict
                )
                # Keep placeholder data - analysis is created but not processed
            
            # Build response
            face_analysis = FaceAnalysisResponse(**face_analysis_dict)
            
            # Convert best_hairstyles from dict to HairstyleRecommendation objects
            best_hairstyles_list = style_recommendations_dict.get("best_hairstyles", [])
            if best_hairstyles_list and isinstance(best_hairstyles_list[0], dict):
                best_hairstyles_list = [HairstyleRecommendation(**item) for item in best_hairstyles_list]
            
            # Remove best_hairstyles from dict to avoid duplicate keyword argument
            style_recommendations_dict_clean = {k: v for k, v in style_recommendations_dict.items() if k != "best_hairstyles"}
            
            style_recommendations = StyleRecommendationsResponse(
                **style_recommendations_dict_clean,
                best_hairstyles=best_hairstyles_list
            )
            personalized_insights = PersonalizedInsightsResponse(**personalized_insights_dict)
            
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
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to create analysis: {e}", exc_info=True)
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
        
        # Remove best_hairstyles from dict to avoid duplicate keyword argument
        style_recommendations_data_clean = {k: v for k, v in style_recommendations_data.items() if k != "best_hairstyles"}
        
        style_recommendations = StyleRecommendationsResponse(
            **style_recommendations_data_clean,
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
            
            # Remove best_hairstyles from dict to avoid duplicate keyword argument
            style_recommendations_data_clean = {k: v for k, v in style_recommendations_data.items() if k != "best_hairstyles"}
            
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
                        **style_recommendations_data_clean,
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

