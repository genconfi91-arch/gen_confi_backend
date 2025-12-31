"""
SQLAlchemy base class and declarative base.
All models should inherit from this base.
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base for all SQLAlchemy models."""
    pass

