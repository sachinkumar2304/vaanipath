from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from app.config import settings
from app.db.supabase_client import supabase

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> dict:
    """
    Validate JWT token and return current user
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        
        if user_id is None or not isinstance(user_id, str):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        
        # If Supabase is not configured, return mock user
        if supabase is None:
            return {
                "id": user_id,
                "email": "mock@user.com",
                "full_name": "Mock User",
                "is_admin": True  # Mock user is admin for testing
            }
        
        # Get user from Supabase
        response = supabase.table("users").select("*").eq("id", user_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        user_data = response.data[0]
        
        # Return only safe, serializable fields
        return {
            "id": user_data.get("id"),
            "email": user_data.get("email"),
            "full_name": user_data.get("full_name"),
            "is_admin": user_data.get("is_admin", False),
            "is_teacher": user_data.get("is_teacher", False),
            "profile_picture_url": user_data.get("profile_picture_url"),
            "bio": user_data.get("bio"),
            "created_at": str(user_data.get("created_at")) if user_data.get("created_at") else None
        }
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


async def get_current_admin(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Check if current user is admin
    """
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user


async def get_current_teacher(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Check if current user is admin or teacher (tutor)
    Allows both admins and teachers to access endpoints
    """
    if not (current_user.get("is_admin", False) or current_user.get("is_teacher", False)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher or admin access required"
        )
    
    return current_user


async def get_current_tutor_only(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Check if current user is a teacher (tutor only, not admin)
    Used for tutor-specific endpoints
    """
    if not current_user.get("is_teacher", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher access required"
        )
    
    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[dict]:
    """
    Get current user if token provided, otherwise return None
    """
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
