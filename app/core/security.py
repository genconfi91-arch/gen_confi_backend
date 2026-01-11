"""
Security utilities for authentication and authorization.
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from app.core.config import settings

# Password hashing context (using bcrypt directly to avoid passlib initialization issues)


def _truncate_password(password: str) -> bytes:
    """
    Truncate password to 72 bytes maximum, handling UTF-8 boundaries.
    
    Args:
        password: The password string to truncate
        
    Returns:
        Password as bytes, guaranteed to be <= 72 bytes
    """
    password_bytes = password.encode('utf-8')
    if len(password_bytes) <= 72:
        return password_bytes
    
    # Truncate to 72 bytes
    truncated_bytes = password_bytes[:72]
    # Remove any incomplete UTF-8 character at the end
    # Continuation bytes start with 10xxxxxx (0b10000000 = 0x80)
    while truncated_bytes and (truncated_bytes[-1] & 0b11000000) == 0b10000000:
        truncated_bytes = truncated_bytes[:-1]
    
    return truncated_bytes


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    
    Bcrypt has a 72-byte limit, so passwords longer than 72 bytes are truncated.
    
    Args:
        plain_password: The plain text password
        hashed_password: The hashed password to verify against
        
    Returns:
        True if password matches, False otherwise
    """
    # Truncate password to 72 bytes if necessary
    password_bytes = _truncate_password(plain_password)
    
    # Use bcrypt directly to avoid passlib initialization issues
    try:
        # Ensure hashed_password is bytes
        if isinstance(hashed_password, str):
            hashed_bytes = hashed_password.encode('utf-8')
        else:
            hashed_bytes = hashed_password
        
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except (ValueError, TypeError):
        # If there's an error, return False (invalid password)
        return False


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Bcrypt has a 72-byte limit, so passwords longer than 72 bytes are truncated.
    
    Args:
        password: The plain text password to hash
        
    Returns:
        The hashed password as a string
    """
    # Truncate password to 72 bytes if necessary
    password_bytes = _truncate_password(password)
    
    # Use bcrypt directly to avoid passlib initialization issues
    # Generate salt and hash the password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Return as string (bcrypt returns bytes)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: The data to encode in the token
        expires_delta: Optional expiration time delta
        
    Returns:
        The encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT access token.
    
    Args:
        token: The JWT token to decode
        
    Returns:
        The decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

