"""
GroomingHistory model definition.
Stores grooming analysis results from groomify_ml service.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class GroomingHistory(Base):
    """
    Model for storing grooming analysis history.
    
    Stores complete analysis results from groomify_ml service,
    including before/after images and full analysis data.
    """
    __tablename__ = "grooming_history"
    
    # Primary key
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )
    
    # Foreign key to users table
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Full analysis data from groomify_ml (JSON)
    analysis_data = Column(
        JSONB,
        nullable=False,
        comment="Complete groomify_ml API response as JSON"
    )
    
    # Image URLs (base64 or file URLs)
    before_image_url = Column(
        String(10000),  # Large enough for base64 strings
        nullable=True,
        comment="Before image URL or base64 encoded string"
    )
    
    after_image_url = Column(
        String(10000),  # Large enough for base64 strings
        nullable=True,
        comment="After image URL or base64 encoded string"
    )
    
    # Status from groomify_ml response
    status = Column(
        String(50),
        nullable=False,
        default="pending",
        comment="Analysis status: success, partial_success, error"
    )
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationship to User model
    user = relationship("User", backref="grooming_history")
    
    # Composite index for efficient user history queries
    __table_args__ = (
        Index('ix_grooming_history_user_created', 'user_id', 'created_at'),
    )
    
    def to_dict(self) -> dict:
        """Convert model instance to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "analysis_data": self.analysis_data,
            "before_image_url": self.before_image_url,
            "after_image_url": self.after_image_url,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

