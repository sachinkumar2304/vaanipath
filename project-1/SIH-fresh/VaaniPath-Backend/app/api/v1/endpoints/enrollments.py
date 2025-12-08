from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.enrollment import (
    EnrollmentCreate,
    EnrollmentResponse,
    EnrollmentList,
    EnrollmentProgress
)
from app.api.deps import get_current_user
from app.db.supabase_client import supabase
import logging
import uuid
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)


def safe_parse_progress(progress_value):
    """Safely parse progress field which may be JSON string or dict"""
    if isinstance(progress_value, str):
        try:
            import json
            return json.loads(progress_value) if progress_value else {}
        except:
            return {}
    elif isinstance(progress_value, dict):
        return progress_value
    else:
        return {}



@router.post("/{course_id}", status_code=status.HTTP_201_CREATED, response_model=EnrollmentResponse)
async def enroll_in_course(
    course_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Enroll in a course (Student only)"""
    try:
        # Check if course exists
        course_response = supabase.table("courses")\
            .select("id, title, thumbnail_url")\
            .eq("id", course_id)\
            .execute()
        
        if not course_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        course = course_response.data[0]
        
        # Check if already enrolled (check both student_id/course_id AND user_id/video_id)
        # First check by course_id and student_id
        existing_enrollment = supabase.table("enrollments")\
            .select("*")\
            .eq("student_id", current_user["id"])\
            .eq("course_id", course_id)\
            .execute()
        
        if existing_enrollment.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already enrolled in this course"
            )

        # Get first video ID for the course (required by DB constraint)
        first_video_response = supabase.table("videos")\
            .select("id")\
            .eq("course_id", course_id)\
            .order("created_at")\
            .limit(1)\
            .execute()
            
        first_video_id = first_video_response.data[0]["id"] if first_video_response.data else None
        
        # Check for existing enrollment by user_id and video_id (to prevent 500 error)
        if first_video_id:
            existing_by_video = supabase.table("enrollments")\
                .select("*")\
                .eq("user_id", current_user["id"])\
                .eq("video_id", first_video_id)\
                .execute()
                
            if existing_by_video.data:
                # If found, it means they are already enrolled, just return the existing one
                # or raise 400. Let's return the existing one to be idempotent/friendly
                # But to be consistent with the other check, let's raise 400
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Already enrolled in this course (verified by video)"
                )
        
        # Create enrollment
        enrollment_id = str(uuid.uuid4())
        enrollment_data = {
            "id": enrollment_id,
            "student_id": current_user["id"],
            "user_id": current_user["id"],  # Required by DB constraint
            "video_id": first_video_id,     # Required by DB constraint
            "course_id": course_id,
            "enrolled_at": datetime.utcnow().isoformat(),
            "progress": {}
        }
        
        try:
            response = supabase.table("enrollments").insert(enrollment_data).execute()
        except Exception as e:
            error_str = str(e).lower()
            if "duplicate key" in error_str or "unique constraint" in error_str:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Already enrolled in this course"
                )
            raise e
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to enroll in course"
            )
        
        enrollment = response.data[0]
        
        # Get video count for the course
        videos_response = supabase.table("videos")\
            .select("id")\
            .eq("course_id", course_id)\
            .execute()
        
        total_videos = len(videos_response.data) if videos_response.data else 0
        
        # Remove computed fields from enrollment dict if they exist to avoid duplicates
        enrollment_dict = {k: v for k, v in enrollment.items() if k not in [
            "course_title", "course_thumbnail", "total_videos", 
            "completed_videos", "progress_percentage"
        ]}
        
        # Ensure progress is always a dict
        if "progress" in enrollment_dict:
            enrollment_dict["progress"] = safe_parse_progress(enrollment_dict["progress"])
        
        return EnrollmentResponse(
            **enrollment_dict,
            course_title=course.get("title"),
            course_thumbnail=course.get("thumbnail_url"),
            total_videos=total_videos,
            completed_videos=0,
            progress_percentage=0.0
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enrolling in course: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/my", response_model=EnrollmentList)
async def get_my_enrollments(
    current_user: dict = Depends(get_current_user)
):
    """Get student's enrolled courses"""
    try:
        # Get enrollments without join first
        response = supabase.table("enrollments")\
            .select("*")\
            .eq("student_id", current_user["id"])\
            .order("enrolled_at", desc=True)\
            .execute()
        
        enrollments = []
        for enrollment in response.data:
            course_id = enrollment.get("course_id")
            
            # Skip enrollments with null/missing course_id (data integrity issue)
            if not course_id:
                logger.warning(f"Skipping enrollment {enrollment.get('id')} - missing course_id")
                continue
            
            # Manually fetch course details
            course_response = supabase.table("courses")\
                .select("title, thumbnail_url")\
                .eq("id", course_id)\
                .execute()
            
            course_data = course_response.data[0] if course_response.data else {}
            
            # Get video count for the course
            videos_response = supabase.table("videos")\
                .select("id")\
                .eq("course_id", course_id)\
                .execute()
            
            total_videos = len(videos_response.data) if videos_response.data else 0
            
            # Calculate completed videos from progress
            progress = enrollment.get("progress", {})
            # Handle progress as either dict or JSON string
            if isinstance(progress, str):
                try:
                    import json
                    progress = json.loads(progress) if progress else {}
                except:
                    progress = {}
            elif not isinstance(progress, dict):
                progress = {}
            
            completed_videos = sum(1 for v in progress.values() if isinstance(v, dict) and v.get("completed", False))
            progress_percentage = (completed_videos / total_videos * 100) if total_videos > 0 else 0.0
            
            # Filter enrollment dict
            enrollment_dict = {k: v for k, v in enrollment.items() if k not in [
                "course_title", "course_thumbnail", "total_videos", 
                "completed_videos", "progress_percentage"
            ]}
            
            # Ensure progress is always a dict
            if "progress" in enrollment_dict:
                enrollment_dict["progress"] = safe_parse_progress(enrollment_dict["progress"])

            try:
                enrollments.append(EnrollmentResponse(
                    **enrollment_dict,
                    course_title=course_data.get("title"),
                    course_thumbnail=course_data.get("thumbnail_url"),
                    total_videos=total_videos,
                    completed_videos=completed_videos,
                    progress_percentage=progress_percentage
                ))
            except Exception as e:
                logger.error(f"Error creating EnrollmentResponse: {e}")
                logger.error(f"Enrollment keys: {enrollment.keys()}")
                logger.error(f"Enrollment dict keys: {enrollment_dict.keys()}")
                raise e
        
        return EnrollmentList(
            enrollments=enrollments,
            total=len(enrollments)
        )
        
    except Exception as e:
        logger.error(f"Error fetching enrollments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{course_id}/progress", response_model=EnrollmentResponse)
async def get_course_progress(
    course_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get progress for a specific course"""
    try:
        # Get enrollment without join
        # Try with student_id first
        response = supabase.table("enrollments")\
            .select("*")\
            .eq("student_id", current_user["id"])\
            .eq("course_id", course_id)\
            .execute()
        
        # Fallback to user_id if not found
        if not response.data:
            response = supabase.table("enrollments")\
                .select("*")\
                .eq("user_id", current_user["id"])\
                .eq("course_id", course_id)\
                .execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enrollment not found"
            )
        
        enrollment = response.data[0]
        
        # Manually fetch course details
        course_response = supabase.table("courses")\
            .select("title, thumbnail_url")\
            .eq("id", course_id)\
            .execute()
            
        course_data = course_response.data[0] if course_response.data else {}
        
        # Get video count
        videos_response = supabase.table("videos")\
            .select("id")\
            .eq("course_id", course_id)\
            .execute()
        
        total_videos = len(videos_response.data) if videos_response.data else 0
        
        # Calculate progress
        progress = enrollment.get("progress", {})
        # Handle progress as either dict or JSON string
        if isinstance(progress, str):
            try:
                import json
                progress = json.loads(progress) if progress else {}
            except:
                progress = {}
        elif not isinstance(progress, dict):
            progress = {}
        
        completed_videos = sum(1 for v in progress.values() if isinstance(v, dict) and v.get("completed", False))
        progress_percentage = (completed_videos / total_videos * 100) if total_videos > 0 else 0.0
        
        # Filter enrollment dict
        enrollment_dict = {k: v for k, v in enrollment.items() if k not in [
            "course_title", "course_thumbnail", "total_videos", 
            "completed_videos", "progress_percentage"
        ]}
        
        # Ensure progress is always a dict
        if "progress" in enrollment_dict:
            enrollment_dict["progress"] = safe_parse_progress(enrollment_dict["progress"])

        return EnrollmentResponse(
            **enrollment_dict,
            course_title=course_data.get("title"),
            course_thumbnail=course_data.get("thumbnail_url"),
            total_videos=total_videos,
            completed_videos=completed_videos,
            progress_percentage=progress_percentage
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching course progress: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{course_id}/progress", response_model=EnrollmentResponse)
async def update_video_progress(
    course_id: str,
    progress_update: EnrollmentProgress,
    current_user: dict = Depends(get_current_user)
):
    """Update progress for a video in a course"""
    try:
        # Get enrollment
        # Try with student_id first
        enrollment_response = supabase.table("enrollments")\
            .select("*")\
            .eq("student_id", current_user["id"])\
            .eq("course_id", course_id)\
            .execute()
        
        # Fallback to user_id if not found
        if not enrollment_response.data:
            enrollment_response = supabase.table("enrollments")\
                .select("*")\
                .eq("user_id", current_user["id"])\
                .eq("course_id", course_id)\
                .execute()
        
        if not enrollment_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enrollment not found"
            )
        
        enrollment = enrollment_response.data[0]
        current_progress = enrollment.get("progress", {})
        # Handle progress as either dict or JSON string
        if isinstance(current_progress, str):
            try:
                import json
                current_progress = json.loads(current_progress) if current_progress else {}
            except:
                current_progress = {}
        elif not isinstance(current_progress, dict):
            current_progress = {}
        
        # Update progress for the video
        current_progress[progress_update.video_id] = {
            "completed": progress_update.completed,
            "watched_duration": progress_update.watched_duration,
            "last_watched_at": datetime.utcnow().isoformat()
        }
        
        # Update enrollment
        update_response = supabase.table("enrollments")\
            .update({"progress": current_progress})\
            .eq("id", enrollment["id"])\
            .execute()
            
        updated_enrollment = update_response.data[0] if update_response.data else enrollment

        # Fetch course data for response
        course_response = supabase.table("courses")\
            .select("title, thumbnail_url")\
            .eq("id", course_id)\
            .execute()
        course_data = course_response.data[0] if course_response.data else {}

        # Get video count
        videos_response = supabase.table("videos")\
            .select("id")\
            .eq("course_id", course_id)\
            .execute()
        
        total_videos = len(videos_response.data) if videos_response.data else 0
        
        # Calculate progress
        completed_videos = sum(1 for v in current_progress.values() if v.get("completed", False))
        progress_percentage = (completed_videos / total_videos * 100) if total_videos > 0 else 0.0
        
        # Filter enrollment dict
        enrollment_dict = {k: v for k, v in updated_enrollment.items() if k not in [
            "course_title", "course_thumbnail", "total_videos", 
            "completed_videos", "progress_percentage"
        ]}
        
        # Ensure progress is always a dict
        if "progress" in enrollment_dict:
            enrollment_dict["progress"] = safe_parse_progress(enrollment_dict["progress"])

        return EnrollmentResponse(
            **enrollment_dict,
            course_title=course_data.get("title"),
            course_thumbnail=course_data.get("thumbnail_url"),
            total_videos=total_videos,
            completed_videos=completed_videos,
            progress_percentage=progress_percentage
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating progress: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unenroll_from_course(
    course_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Unenroll from a course"""
    try:
        # Check if enrolled
        # Try with student_id first
        enrollment_response = supabase.table("enrollments")\
            .select("*")\
            .eq("student_id", current_user["id"])\
            .eq("course_id", course_id)\
            .execute()
        
        # Fallback to user_id if not found
        if not enrollment_response.data:
            enrollment_response = supabase.table("enrollments")\
                .select("*")\
                .eq("user_id", current_user["id"])\
                .eq("course_id", course_id)\
                .execute()
        
        if not enrollment_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enrollment not found"
            )
        
        # Delete enrollment
        supabase.table("enrollments")\
            .delete()\
            .eq("id", enrollment_response.data[0]["id"])\
            .execute()
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unenrolling: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
