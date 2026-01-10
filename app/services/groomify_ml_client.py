"""
Groomify ML service client for communicating with the groomify_ml microservice.

This module handles all HTTP communication with the groomify_ml API,
including error handling, retries, and response validation.
"""
import httpx
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings

logger = logging.getLogger(__name__)


class GroomifyMLClient:
    """
    Client for communicating with the groomify_ml microservice.
    
    Handles image analysis requests, error handling, and retries.
    """
    
    def __init__(self):
        """Initialize the groomify_ml client with configuration."""
        self.base_url = settings.GROOMIFY_ML_API_URL.rstrip('/')
        self.timeout = settings.GROOMIFY_ML_TIMEOUT
        self.retry_count = settings.GROOMIFY_ML_RETRY_COUNT
        self.analyze_endpoint = f"{self.base_url}/analyze/user"
        
    async def analyze_user(
        self,
        image_file: UploadFile,
        gender: str
    ) -> Dict[str, Any]:
        """
        Send user image and gender to groomify_ml for analysis.
        
        Args:
            image_file: Uploaded image file to analyze
            gender: User gender ("male" or "female")
            
        Returns:
            Dictionary containing analysis results from groomify_ml
            
        Raises:
            HTTPException: If the request fails after all retries
        """
        # Validate gender
        gender_lower = gender.lower()
        if gender_lower not in ["male", "female"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid gender '{gender}'. Must be 'male' or 'female'."
            )
        
        # Read image file content
        try:
            image_content = await image_file.read()
            # Reset file pointer for potential retries
            await image_file.seek(0)
        except Exception as e:
            logger.error(f"Failed to read image file: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to read image file: {str(e)}"
            )
        
        # Prepare multipart form data
        files = {
            "file": (image_file.filename, image_content, image_file.content_type)
        }
        data = {
            "gender": gender_lower
        }
        
        # Retry logic
        last_exception = None
        for attempt in range(self.retry_count + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    logger.info(
                        f"Calling groomify_ml API (attempt {attempt + 1}/{self.retry_count + 1}): "
                        f"{self.analyze_endpoint}"
                    )
                    
                    response = await client.post(
                        self.analyze_endpoint,
                        files=files,
                        data=data
                    )
                    
                    # Check if request was successful
                    response.raise_for_status()
                    
                    # Parse JSON response
                    result = response.json()
                    
                    logger.info(
                        f"Successfully received analysis from groomify_ml: "
                        f"status={result.get('status')}, user_id={result.get('user_id')}"
                    )
                    
                    return result
                    
            except httpx.TimeoutException as e:
                last_exception = e
                logger.warning(
                    f"Groomify_ml API timeout (attempt {attempt + 1}/{self.retry_count + 1}): {e}"
                )
                if attempt < self.retry_count:
                    continue
                    
            except httpx.HTTPStatusError as e:
                last_exception = e
                logger.error(
                    f"Groomify_ml API HTTP error (attempt {attempt + 1}/{self.retry_count + 1}): "
                    f"status={e.response.status_code}, detail={e.response.text}"
                )
                # Don't retry on client errors (4xx)
                if 400 <= e.response.status_code < 500:
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"Groomify_ml service error: {e.response.text}"
                    )
                if attempt < self.retry_count:
                    continue
                    
            except httpx.RequestError as e:
                last_exception = e
                logger.error(
                    f"Groomify_ml API request error (attempt {attempt + 1}/{self.retry_count + 1}): {e}"
                )
                if attempt < self.retry_count:
                    continue
                    
            except Exception as e:
                last_exception = e
                logger.error(
                    f"Unexpected error calling groomify_ml API (attempt {attempt + 1}/{self.retry_count + 1}): {e}",
                    exc_info=True
                )
                if attempt < self.retry_count:
                    continue
        
        # All retries failed
        error_msg = f"Failed to get analysis from groomify_ml after {self.retry_count + 1} attempts"
        if last_exception:
            error_msg += f": {str(last_exception)}"
        
        logger.error(error_msg)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=error_msg
        )
    
    async def health_check(self) -> bool:
        """
        Check if groomify_ml service is available.
        
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            health_url = f"{self.base_url}/health"
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(health_url)
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"Groomify_ml health check failed: {e}")
            return False

