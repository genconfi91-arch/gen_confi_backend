"""
Analysis repository for database operations.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.analysis import UserAnalysis


class AnalysisRepository:
    """Repository for user analysis operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user_id: int, image_path: str, chat_answers: dict) -> UserAnalysis:
        """
        Create a new analysis record.
        
        Args:
            user_id: User ID
            image_path: Path to uploaded image
            chat_answers: Chat question answers as dictionary
            
        Returns:
            Created UserAnalysis object
        """
        analysis = UserAnalysis(
            user_id=user_id,
            image_path=image_path,
            chat_answers=chat_answers
        )
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        return analysis
    
    def get_by_id(self, analysis_id: int) -> Optional[UserAnalysis]:
        """
        Get analysis by ID.
        
        Args:
            analysis_id: Analysis ID
            
        Returns:
            UserAnalysis object or None
        """
        return self.db.query(UserAnalysis).filter(UserAnalysis.id == analysis_id).first()
    
    def get_by_user_id(self, user_id: int, limit: int = 10, skip: int = 0) -> List[UserAnalysis]:
        """
        Get all analyses for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of results
            skip: Number of results to skip
            
        Returns:
            List of UserAnalysis objects
        """
        return (
            self.db.query(UserAnalysis)
            .filter(UserAnalysis.user_id == user_id)
            .order_by(UserAnalysis.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def update_face_analysis(self, analysis_id: int, face_analysis: dict) -> Optional[UserAnalysis]:
        """
        Update face analysis results (for model integration).
        
        Args:
            analysis_id: Analysis ID
            face_analysis: Face analysis results as dictionary
            
        Returns:
            Updated UserAnalysis object or None
        """
        analysis = self.get_by_id(analysis_id)
        if analysis:
            analysis.face_analysis = face_analysis
            self.db.commit()
            self.db.refresh(analysis)
        return analysis
    
    def update_style_recommendations(
        self, 
        analysis_id: int, 
        style_recommendations: dict
    ) -> Optional[UserAnalysis]:
        """
        Update style recommendations (for model integration).
        
        Args:
            analysis_id: Analysis ID
            style_recommendations: Style recommendations as dictionary
            
        Returns:
            Updated UserAnalysis object or None
        """
        analysis = self.get_by_id(analysis_id)
        if analysis:
            analysis.style_recommendations = style_recommendations
            self.db.commit()
            self.db.refresh(analysis)
        return analysis
    
    def update_personalized_insights(
        self, 
        analysis_id: int, 
        personalized_insights: dict
    ) -> Optional[UserAnalysis]:
        """
        Update personalized insights (for model integration).
        
        Args:
            analysis_id: Analysis ID
            personalized_insights: Personalized insights as dictionary
            
        Returns:
            Updated UserAnalysis object or None
        """
        analysis = self.get_by_id(analysis_id)
        if analysis:
            analysis.personalized_insights = personalized_insights
            self.db.commit()
            self.db.refresh(analysis)
        return analysis
    
    def update(
        self,
        analysis_id: int,
        face_analysis: Optional[dict] = None,
        style_recommendations: Optional[dict] = None,
        personalized_insights: Optional[dict] = None
    ) -> Optional[UserAnalysis]:
        """
        Update analysis results (all fields at once).
        
        Args:
            analysis_id: Analysis ID
            face_analysis: Face analysis results as dictionary (optional)
            style_recommendations: Style recommendations as dictionary (optional)
            personalized_insights: Personalized insights as dictionary (optional)
            
        Returns:
            Updated UserAnalysis object or None
        """
        analysis = self.get_by_id(analysis_id)
        if analysis:
            if face_analysis is not None:
                analysis.face_analysis = face_analysis
            if style_recommendations is not None:
                analysis.style_recommendations = style_recommendations
            if personalized_insights is not None:
                analysis.personalized_insights = personalized_insights
            self.db.commit()
            self.db.refresh(analysis)
        return analysis

