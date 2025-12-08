from fastapi import APIRouter, HTTPException, status, Depends
from app.models.user import UserCreate, UserLogin, UserResponse, Token
from app.core.security import create_access_token, verify_password, get_password_hash
from app.api.deps import get_current_user
from app.db.supabase_client import supabase
from app.config import settings
from datetime import datetime
import logging
import uuid

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate):
    """
    Register a new user
    """
    try:
        # Check if Supabase is configured
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            logger.warning("Supabase not configured, returning mock response")
            # Return mock user for frontend testing
            user_id = str(uuid.uuid4())
            return {
                "id": user_id,
                "email": user.email,
                "full_name": user.full_name,
                "is_admin": user.is_admin,
                "created_at": datetime.utcnow().isoformat(),
                "message": "Database not configured - mock response"
            }
        
        # Check if user already exists
        existing = supabase.table("users").select("*").eq("email", user.email).execute()
        
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = get_password_hash(user.password)
        
        # Create user - let Supabase generate UUID
        user_data = {
            "email": user.email,
            "full_name": user.full_name,
            "password_hash": hashed_password,
            "is_admin": user.is_admin,
            "is_teacher": False
        }
        
        try:
            response = supabase.table("users").insert(user_data).execute()
            
            if not response.data:
                logger.error(f"Supabase insert returned no data: {response}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user"
                )
            
            # Award 100 GyanPoints on Signup
            try:
                from app.features.community.services.gyan_points_service import GyanPointsService
                created_user_id = response.data[0]['id']
                await GyanPointsService.add_points(
                    user_id=created_user_id,
                    points=100,
                    source="signup_bonus",
                    description="Welcome Bonus: 100 GyanPoints for joining VaaniPath!",
                    reference_id=None
                )
            except Exception as e:
                logger.error(f"Failed to award signup points: {e}")
                # Don't fail signup if points fail, but log it.

            logger.info(f"✅ User created: {user.email}")
            return response.data[0]
        except Exception as db_error:
            logger.error(f"❌ Database error during signup: {db_error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create user: {str(db_error)}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logger.error(f"❌ Signup error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """
    Login and get access token
    """
    try:
        # Check if Supabase is configured
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            logger.warning("Supabase not configured, returning mock token")
            # Create mock token for frontend testing
            mock_user_id = str(uuid.uuid4())
            access_token = create_access_token(data={"sub": mock_user_id})
            return {
                "access_token": access_token,
                "token_type": "bearer"
            }
        
        # Get user by email - select only needed fields to avoid JSON serialization issues
        try:
            response = supabase.table("users").select("id, email, password_hash, is_admin, is_teacher, full_name").eq("email", credentials.email).execute()
            
            if not response.data:
                logger.warning(f"User not found: {credentials.email}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password"
                )
            
            user = response.data[0]
            
            # Verify password
            if not verify_password(credentials.password, user["password_hash"]):
                logger.warning(f"Invalid password for user: {credentials.email}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password"
                )
            
            # Create access token
            access_token = create_access_token(data={"sub": user["id"]})
            logger.info(f"✅ User logged in: {credentials.email}")
            
            # Construct response
            user_response = {
                "id": user["id"],
                "email": user["email"],
                "full_name": user["full_name"],
                "user_type": "admin" if user.get("is_admin") else ("teacher" if user.get("is_teacher") else "student"),
                "is_teacher": user.get("is_teacher", False),
                "is_admin": user.get("is_admin", False),
                "avatar_url": None, # user.get("profile_picture_url"),
                "created_at": datetime.utcnow() # user.get("created_at", datetime.utcnow())
            }
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": user_response
            }
        except HTTPException:
            raise
        except Exception as db_error:
            logger.error(f"❌ Database error during login: {db_error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Login failed: {str(db_error)}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current user information
    """
    return current_user
