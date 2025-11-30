from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from app.config import settings
import hashlib

# Password hashing context - use argon2 which doesn't have 72-byte limit
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")


def _hash_password_for_bcrypt(password: str) -> str:
    """
    Hash password with SHA256 first to handle long passwords,
    then bcrypt can handle the hash
    """
    # SHA256 hash the password first (always 64 chars)
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except ValueError:
        # If bcrypt fails due to length, try SHA256 approach
        sha_hash = _hash_password_for_bcrypt(plain_password)
        return pwd_context.verify(sha_hash, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using argon2"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt
