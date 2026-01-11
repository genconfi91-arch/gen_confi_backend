"""
UserFeatures model definition for storing extracted facial features from groomify_ml.
This model stores the analysis results from the AI styling system.
"""
from sqlalchemy import Column, String, Float, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class UserFeatures(Base):
    """
    Model for storing extracted user facial features from groomify_ml analysis.
    
    Note: Images are NOT stored, only extracted metrics.
    This table is populated by the groomify_ml service.
    """
    __tablename__ = "user_features"
    
    # Primary key - using UUID string for compatibility
    user_id = Column(
        String(36),  # UUID as string
        primary_key=True,
        index=True
    )
    
    # Optional: Link to User table if you want to associate with registered users
    # If None, this is an anonymous analysis
    gen_confi_user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Gender (required for conditional analysis)
    gender = Column(String(10), nullable=False)  # "male" or "female"
    
    # Face metrics
    face_shape = Column(String(50), nullable=True)
    face_length = Column(Float, nullable=True)
    face_width = Column(Float, nullable=True)
    forehead_width = Column(Float, nullable=True)
    jaw_width = Column(Float, nullable=True)
    chin_length = Column(Float, nullable=True)
    
    # Skin analysis
    skin_tone = Column(String(50), nullable=True)
    undertone = Column(String(50), nullable=True)
    ita_score = Column(Float, nullable=True)
    
    # Hair analysis
    hairline_type = Column(String(50), nullable=True)
    recession_level = Column(String(50), nullable=True)
    hair_texture = Column(String(50), nullable=True)
    
    # Male-specific: Beard analysis
    beard_type = Column(String(50), nullable=True)  # e.g., "Full", "Goatee", "Stubble", "None"
    beard_density = Column(String(50), nullable=True)  # e.g., "Thick", "Medium", "Sparse", "None"
    
    # Female-specific: Eyebrow analysis
    eyebrow_shape = Column(String(50), nullable=True)  # e.g., "Straight", "Arched", "Rounded", "S-Shaped"
    
    # Timestamp
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationship to User model (optional)
    user = relationship("User", backref="features")
    
    def to_dict(self) -> dict:
        """Convert model instance to dictionary."""
        return {
            "user_id": self.user_id,
            "gen_confi_user_id": self.gen_confi_user_id,
            "gender": self.gender,
            "face_shape": self.face_shape,
            "face_length": self.face_length,
            "face_width": self.face_width,
            "forehead_width": self.forehead_width,
            "jaw_width": self.jaw_width,
            "chin_length": self.chin_length,
            "skin_tone": self.skin_tone,
            "undertone": self.undertone,
            "ita_score": self.ita_score,
            "hairline_type": self.hairline_type,
            "recession_level": self.recession_level,
            "hair_texture": self.hair_texture,
            "beard_type": self.beard_type,
            "beard_density": self.beard_density,
            "eyebrow_shape": self.eyebrow_shape,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

