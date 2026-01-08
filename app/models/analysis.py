"""
Analysis model definition.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class UserAnalysis(Base):
    """
    User analysis model representing a complete analysis session.
    
    Attributes:
        id: Primary key, auto-incrementing integer
        user_id: Foreign key to users table
        image_path: Path to uploaded image
        chat_answers: JSON field storing chat question answers
        face_analysis: JSON field for face analysis results (placeholder for model integration)
        style_recommendations: JSON field for style recommendations (placeholder for model integration)
        created_at: Timestamp when analysis was created
        updated_at: Timestamp when analysis was last updated
    """
    __tablename__ = "user_analyses"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    image_path = Column(String(500), nullable=False)
    chat_answers = Column(JSON, nullable=False)
    
    # Placeholder fields for model integration (will be populated later)
    face_analysis = Column(JSON, nullable=True)
    style_recommendations = Column(JSON, nullable=True)
    personalized_insights = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationship to User model
    user = relationship("User", backref="analyses")

