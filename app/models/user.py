"""
User model definition.
"""
import enum
from sqlalchemy import Column, Integer, String, Enum as SQLEnum
from app.db.base import Base


class UserRole(str, enum.Enum):
    """User role enumeration."""
    CLIENT = "client"
    EXPERT = "expert"
    ADMIN = "admin"


class User(Base):
    """
    User model representing a user in the system.
    
    Attributes:
        id: Primary key, auto-incrementing integer
        email: Unique email address
        name: User's full name
        phone: User's phone number
        password: Hashed password
        role: User role (client, expert, admin)
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole, native_enum=False, values_callable=lambda x: [e.value for e in x]), default=UserRole.CLIENT, nullable=False)
    avatar_url = Column(String(500), nullable=True)
    gender = Column(String(20), nullable=True)

