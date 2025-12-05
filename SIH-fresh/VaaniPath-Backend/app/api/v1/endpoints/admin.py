from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict
from app.api.deps import get_current_admin
from app.models.user import TutorCreate, TutorResponse
from app.core.security import get_password_hash
from app.db.supabase_client import supabase
from app.config import settings
import logging
import uuid
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/stats")
async def get_admin_stats(
    current_user: dict = Depends(get_current_admin)
):
    """
    Get admin dashboard statistics - LIVE DATA from Supabase
    """
    try:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            logger.warning("Supabase not configured, returning empty stats")
            return {
                "total_videos": 0,
                "videos_by_status": {
                    "completed": 0,
                    "processing": 0,
                    "failed": 0,
                    "pending": 0
                },
                "total_users": 0,
                "total_students": 0,
                "total_teachers": 0
            }
        
        # Get total users count
        users_response = supabase.table("users").select("id", count="exact").execute()
        total_users = users_response.count if users_response.count is not None else 0
        
        # Get teachers count (is_teacher = TRUE)
        teachers_response = supabase.table("users").select("id", count="exact").eq("is_teacher", True).execute()
        total_teachers = teachers_response.count if teachers_response.count is not None else 0
        
        # Get students count (is_teacher = FALSE AND is_admin = FALSE)
        students_response = supabase.table("users").select("id", count="exact").eq("is_teacher", False).eq("is_admin", False).execute()
        total_students = students_response.count if students_response.count is not None else 0
        
        # Get total videos count (if videos table exists)
        try:
            videos_response = supabase.table("videos").select("id, status", count="exact").execute()
            total_videos = videos_response.count if videos_response.count is not None else 0
            
            # Count videos by status
            videos_by_status = {
                "completed": 0,
                "processing": 0,
                "failed": 0,
                "pending": 0
            }
            
            if videos_response.data:
                for video in videos_response.data:
                    video_status = video.get("status", "pending").lower()
                    if video_status in videos_by_status:
                        videos_by_status[video_status] += 1
        except Exception as video_error:
            logger.warning(f"Videos table might not exist yet: {video_error}")
            total_videos = 0
            videos_by_status = {
                "completed": 0,
                "processing": 0,
                "failed": 0,
                "pending": 0
            }
        
        logger.info(f"✅ Stats fetched - Users: {total_users}, Teachers: {total_teachers}, Students: {total_students}, Videos: {total_videos}")
        
        return {
            "total_videos": total_videos,
            "videos_by_status": videos_by_status,
            "total_users": total_users,
            "total_students": total_students,
            "total_teachers": total_teachers
        }
    
    except Exception as e:
        logger.error(f"❌ Error fetching admin stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch stats: {str(e)}"
        )


@router.get("/users")
async def list_all_users(
    current_user: dict = Depends(get_current_admin)
):
    """
    List all users (Admin only)
    """
    # Mock data for frontend testing
    # TODO: Replace with actual Supabase query
    return {
        "users": [
            {
                "id": current_user.get("user_id"),
                "email": current_user.get("email", "admin@example.com"),
                "full_name": current_user.get("full_name", "Admin User"),
                "is_admin": True,
                "created_at": "2025-11-17T00:00:00Z"
            }
        ],
        "total": 1
    }


@router.patch("/users/{user_id}/admin")
async def toggle_admin_status(
    user_id: str,
    is_admin: bool,
    current_user: dict = Depends(get_current_admin)
):
    """
    Make a user admin or remove admin privileges
    """
    # Mock response for frontend testing
    # TODO: Replace with actual Supabase update
    return {
        "message": "Admin status updated successfully",
        "user_id": user_id,
        "is_admin": is_admin
    }


@router.post("/create-tutor", response_model=TutorResponse, status_code=status.HTTP_201_CREATED)
async def create_tutor(
    tutor: TutorCreate,
    current_user: dict = Depends(get_current_admin)
):
    """
    Create a new tutor account (Super Admin only)
    Tutors cannot self-register - only admins can create tutor accounts
    """
    try:
        # Check if Supabase is configured
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            logger.warning("Supabase not configured, returning mock response")
            tutor_id = str(uuid.uuid4())
            return {
                "id": tutor_id,
                "email": tutor.email,
                "full_name": tutor.full_name,
                "is_teacher": True,
                "created_at": datetime.utcnow().isoformat(),
                "temporary_password": tutor.password
            }
        
        # Check if email already exists
        existing = supabase.table("users").select("*").eq("email", tutor.email).execute()
        
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = get_password_hash(tutor.password)
        
        # Create tutor user with is_teacher = TRUE
        tutor_data = {
            "email": tutor.email,
            "full_name": tutor.full_name,
            "password_hash": hashed_password,
            "is_admin": False,
            "is_teacher": True  # THIS IS THE KEY FIELD!
        }
        
        try:
            response = supabase.table("users").insert(tutor_data).execute()
            
            if not response.data:
                logger.error(f"Supabase insert returned no data: {response}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create tutor"
                )
            
            created_tutor = response.data[0]
            logger.info(f"✅ Tutor created: {tutor.email}")
            
            # Return tutor data with temporary password for admin to share
            return {
                "id": created_tutor["id"],
                "email": created_tutor["email"],
                "full_name": created_tutor["full_name"],
                "is_teacher": True,
                "created_at": created_tutor["created_at"],
                "temporary_password": tutor.password  # Return plain password to admin
            }
        except Exception as db_error:
            logger.error(f"❌ Database error during tutor creation: {db_error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create tutor: {str(db_error)}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logger.error(f"❌ Create tutor error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/tutors")
async def list_tutors(
    current_user: dict = Depends(get_current_admin)
):
    """
    List all tutors with their stats
    """
    try:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            return {
                "tutors": [],
                "total": 0
            }
        
        # Query users where is_teacher = TRUE
        response = supabase.table("users").select("id, email, full_name, created_at").eq("is_teacher", True).execute()
        
        return {
            "tutors": response.data if response.data else [],
            "total": len(response.data) if response.data else 0
        }
    except Exception as e:
        logger.error(f"List tutors error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/students")
async def list_students(
    current_user: dict = Depends(get_current_admin)
):
    """
    List all students (non-admin, non-teacher users)
    """
    try:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            return {
                "students": [],
                "total": 0
            }
        
        # Query users where is_teacher = FALSE AND is_admin = FALSE
        response = supabase.table("users").select("id, email, full_name, created_at").eq("is_teacher", False).eq("is_admin", False).execute()
        
        return {
            "students": response.data if response.data else [],
            "total": len(response.data) if response.data else 0
        }
    except Exception as e:
        logger.error(f"List students error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.patch("/users/{user_id}/teacher")
async def toggle_teacher_status(
    user_id: str,
    is_teacher: bool,
    current_user: dict = Depends(get_current_admin)
):
    """
    Make a user a teacher or remove teacher privileges
    """
    try:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            return {
                "message": "Teacher status updated (mock)",
                "user_id": user_id,
                "is_teacher": is_teacher
            }
        
        response = supabase.table("users").update({"is_teacher": is_teacher}).eq("id", user_id).execute()
        
        return {
            "message": "Teacher status updated successfully",
            "user_id": user_id,
            "is_teacher": is_teacher
        }
    except Exception as e:
        logger.error(f"Toggle teacher status error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/jobs/active")
async def get_active_jobs(
    current_user: dict = Depends(get_current_admin)
):
    """
    Get all active processing jobs
    """
    # Mock data for frontend testing
    # TODO: Replace with actual Redis/Celery query
    return {
        "active_jobs": [],
        "total": 0
    }


@router.post("/jobs/{job_id}/cancel")
async def cancel_job(
    job_id: str,
    current_user: dict = Depends(get_current_admin)
):
    """
    Cancel a processing job
    """
    # Mock response for frontend testing
    # TODO: Replace with actual Celery task revocation
    return {
        "message": "Job cancelled successfully",
        "job_id": job_id,
        "status": "cancelled"
    }


@router.delete("/tutors/{tutor_id}", status_code=status.HTTP_200_OK)
async def delete_tutor(
    tutor_id: str,
    current_user: dict = Depends(get_current_admin)
):
    """
    Delete a tutor account and all associated data (Admin only)
    
    This will CASCADE delete:
    - All courses created by the tutor
    - All videos uploaded by the tutor
    - All enrollments related to those courses/videos
    - All transcriptions, translations, subtitles
    - All quiz questions and responses
    - All reviews and processing jobs
    
    This action is PERMANENT and cannot be undone.
    """
    try:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database not configured"
            )
        
        # Prevent admin from deleting themselves
        if tutor_id == current_user.get("id"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        # Check if user exists and is a teacher
        user_response = supabase.table("users").select("id, email, full_name, is_teacher").eq("id", tutor_id).execute()
        
        if not user_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tutor not found"
            )
        
        user = user_response.data[0]
        
        if not user.get("is_teacher"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not a tutor"
            )
        
        # Get counts of data that will be deleted (for logging/response)
        courses_response = supabase.table("courses").select("id", count="exact").eq("teacher_id", tutor_id).execute()
        courses_count = courses_response.count if courses_response.count is not None else 0
        
        videos_response = supabase.table("videos").select("id", count="exact").eq("uploaded_by", tutor_id).execute()
        videos_count = videos_response.count if videos_response.count is not None else 0
        
        # Delete the user - CASCADE will handle all related data
        supabase.table("users").delete().eq("id", tutor_id).execute()
        
        logger.info(f"✅ Deleted tutor {user['email']} (ID: {tutor_id})")
        logger.info(f"   - Courses deleted: {courses_count}")
        logger.info(f"   - Videos deleted: {videos_count}")
        
        return {
            "message": "Tutor deleted successfully",
            "tutor_email": user["email"],
            "tutor_name": user["full_name"],
            "deleted_resources": {
                "courses": courses_count,
                "videos": videos_count
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting tutor: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete tutor: {str(e)}"
        )

