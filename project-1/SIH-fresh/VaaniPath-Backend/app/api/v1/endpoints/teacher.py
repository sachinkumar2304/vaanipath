from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_current_teacher
from app.db.supabase_client import supabase
from app.config import settings
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/stats")
async def get_teacher_stats(
    current_user: dict = Depends(get_current_teacher)
):
    """
    Get teacher dashboard statistics
    """
    try:
        if not supabase or not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            logger.error("❌ Supabase not configured")
            return {
                "total_videos": 0,
                "total_students": 0,
                "total_views": 0
            }
        
        teacher_id = current_user.get("id")
        
        # Get total videos uploaded by teacher
        videos_response = supabase.table("videos")\
            .select("id", count="exact")\
            .eq("uploaded_by", teacher_id)\
            .execute()
        
        total_videos = videos_response.count if videos_response.count is not None else 0
        
        # Get total students enrolled in teacher's videos
        # First get video IDs
        teacher_videos = supabase.table("videos")\
            .select("id")\
            .eq("uploaded_by", teacher_id)\
            .execute()
        
        video_ids = [v["id"] for v in (teacher_videos.data or [])]
        
        total_students = 0
        if video_ids:
            try:
                # Count unique students enrolled in these videos
                enrollments = supabase.table("enrollments")\
                    .select("user_id")\
                    .in_("video_id", video_ids)\
                    .execute()
                
                # Get unique student IDs
                unique_students = set()
                for enrollment in (enrollments.data or []):
                    unique_students.add(enrollment["user_id"])
                
                total_students = len(unique_students)
            except Exception as e:
                logger.warning(f"Error counting students: {e}")
        
        logger.info(f"✅ Teacher stats - Videos: {total_videos}, Students: {total_students}")
        
        return {
            "total_videos": total_videos,
            "total_students": total_students,
            "total_views": 0  # TODO: Add views tracking later
        }
    
    except Exception as e:
        logger.error(f"Get teacher stats error: {e}")
        raise HTTPException(
           status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
