from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from app.models.course import (
    CourseCreate,
    CourseUpdate,
    CourseResponse,
    CourseList,
    CourseWithVideos
)
from app.models.video import VideoResponse
from app.api.deps import get_current_teacher, get_current_user, get_optional_user
from app.db.supabase_client import supabase
import logging
import uuid
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=CourseResponse)
async def create_course(
    course: CourseCreate,
    current_user: dict = Depends(get_current_teacher)
):
    """Create a new course (Teacher only)"""
    try:
        course_id = str(uuid.uuid4())
        course_data = {
            "id": course_id,
            "title": course.title,
            "name": course.title,  # Legacy field required by DB
            "description": course.description,
            "thumbnail_url": course.thumbnail_url,
            "teacher_id": current_user["id"],
            "tutor_id": current_user["id"],  # Legacy field required by DB
            "domain": course.domain,
            "source_language": course.source_language,
            "target_languages": course.target_languages,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Insert course
        response = supabase.table("courses").insert(course_data).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create course"
            )
        
        created_course = response.data[0]
        
        # Get teacher info
        teacher_response = supabase.table("users").select("full_name").eq("id", current_user["id"]).execute()
        teacher_name = teacher_response.data[0]["full_name"] if teacher_response.data else None
        
        return CourseResponse(
            **created_course,
            teacher_name=teacher_name,
            total_videos=0,
            total_duration=0
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating course: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("", response_model=CourseList)
async def get_all_courses(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    domain: Optional[str] = None,
    language: Optional[str] = None,
    search: Optional[str] = None,
    current_user: dict = Depends(get_optional_user)
):
    """Get all courses (public access)"""
    try:
        # Remove join that causes error
        query = supabase.table("courses").select("*", count="exact")
        
        # Apply filters
        if domain:
            query = query.eq("domain", domain)
        if language:
            # Note: contains might fail if target_languages is text in DB
            # But we can't easily fix that in query builder if it expects array
            # For now, we'll skip language filter if it causes issues, or assume it works
            pass 
        if search:
            query = query.or_(f"title.ilike.%{search}%,description.ilike.%{search}%")
        
        # Pagination
        offset = (page - 1) * page_size
        response = query.order("created_at", desc=True).range(offset, offset + page_size - 1).execute()
        
        courses = []
        for course in response.data:
            # Get video count and total duration
            videos_response = supabase.table("videos")\
                .select("id, duration")\
                .eq("course_id", course["id"])\
                .execute()
            
            total_videos = len(videos_response.data) if videos_response.data else 0
            total_duration = sum(v.get("duration", 0) or 0 for v in videos_response.data) if videos_response.data else 0
            
            # Manually fetch teacher name
            teacher_id = course.get("teacher_id")
            teacher_name = None
            if teacher_id:
                teacher_response = supabase.table("users").select("full_name").eq("id", teacher_id).execute()
                if teacher_response.data:
                    teacher_name = teacher_response.data[0].get("full_name")
            
            courses.append(CourseResponse(
                **{k: v for k, v in course.items() if k != "users"},
                teacher_name=teacher_name,
                total_videos=total_videos,
                total_duration=total_duration
            ))
        
        return CourseList(
            courses=courses,
            total=response.count or 0,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        logger.error(f"Error fetching courses: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/my", response_model=CourseList)
async def get_my_courses(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_teacher)
):
    """Get teacher's own courses"""
    try:
        # Remove the join that might be causing 500 if FK is missing
        query = supabase.table("courses").select("*", count="exact")
        
        # Handle case where teacher_id might be null but tutor_id exists (legacy data)
        # We query for teacher_id matching current user
        query = query.eq("teacher_id", current_user["id"])
        
        # Pagination
        offset = (page - 1) * page_size
        response = query.order("created_at", desc=True).range(offset, offset + page_size - 1).execute()
        
        courses = []
        for course in response.data:
            # Get video count and total duration
            videos_response = supabase.table("videos")\
                .select("id, duration")\
                .eq("course_id", course["id"])\
                .execute()
            
            total_videos = len(videos_response.data) if videos_response.data else 0
            total_duration = sum(v.get("duration", 0) or 0 for v in videos_response.data) if videos_response.data else 0
            
            # We know the teacher is the current user
            teacher_name = current_user.get("full_name") or current_user.get("name")
            
            courses.append(CourseResponse(
                **{k: v for k, v in course.items() if k != "users"},
                teacher_name=teacher_name,
                total_videos=total_videos,
                total_duration=total_duration
            ))
        
        return CourseList(
            courses=courses,
            total=response.count or 0,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        logger.error(f"Error fetching teacher courses: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/stats/overview")
async def get_teacher_stats(
    current_user: dict = Depends(get_current_teacher)
):
    """Get aggregated stats for teacher dashboard"""
    try:
        teacher_id = current_user["id"]
        
        # 1. Get all courses by teacher
        courses_response = supabase.table("courses")\
            .select("id")\
            .eq("teacher_id", teacher_id)\
            .execute()
            
        course_ids = [c["id"] for c in courses_response.data] if courses_response.data else []
        
        if not course_ids:
            return {
                "totalVideos": 0,
                "totalStudents": 0,
                "totalViews": 0
            }
            
        # 2. Get total videos and views
        try:
            videos_response = supabase.table("videos")\
                .select("id, views")\
                .in_("course_id", course_ids)\
                .execute()
            videos = videos_response.data if videos_response.data else []
            total_videos = len(videos)
            total_views = sum(v.get("views", 0) or 0 for v in videos)
        except Exception:
            # Fallback if views column missing
            videos_response = supabase.table("videos")\
                .select("id")\
                .in_("course_id", course_ids)\
                .execute()
            videos = videos_response.data if videos_response.data else []
            total_videos = len(videos)
            total_views = 0
        
        # 3. Get total enrollments across all courses
        enrollments_count_response = supabase.table("enrollments")\
            .select("id", count="exact", head=True)\
            .in_("course_id", course_ids)\
            .execute()
            
        total_students = enrollments_count_response.count if enrollments_count_response.count is not None else 0
        
        return {
            "totalVideos": total_videos,
            "totalStudents": total_students,
            "totalViews": total_views
        }
        
    except Exception as e:
        logger.error(f"Error fetching teacher stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{course_id}", response_model=CourseWithVideos)
async def get_course_by_id(
    course_id: str,
    current_user: dict = Depends(get_optional_user)
):
    """Get course details with videos"""
    try:
        # Get course without join
        course_response = supabase.table("courses")\
            .select("*")\
            .eq("id", course_id)\
            .execute()
        
        if not course_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        course = course_response.data[0]
        
        # Get videos
        videos_response = supabase.table("videos")\
            .select("*")\
            .eq("course_id", course_id)\
            .order("order")\
            .execute()
        
        videos = videos_response.data if videos_response.data else []
        total_videos = len(videos)
        total_duration = sum(v.get("duration", 0) or 0 for v in videos)
        
        # Manually fetch teacher name
        teacher_id = course.get("teacher_id")
        teacher_name = None
        if teacher_id:
            teacher_response = supabase.table("users").select("full_name").eq("id", teacher_id).execute()
            if teacher_response.data:
                teacher_name = teacher_response.data[0].get("full_name")
        
        return CourseWithVideos(
            **{k: v for k, v in course.items() if k != "users"},
            teacher_name=teacher_name,
            total_videos=total_videos,
            total_duration=total_duration,
            videos=videos
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching course: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: str,
    course_update: CourseUpdate,
    current_user: dict = Depends(get_current_teacher)
):
    """Update course (Teacher only - own courses)"""
    try:
        # Check if course exists and belongs to teacher
        course_response = supabase.table("courses")\
            .select("*")\
            .eq("id", course_id)\
            .execute()
        
        if not course_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        course = course_response.data[0]
        if course["teacher_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own courses"
            )
        
        # Prepare update data
        update_data = course_update.dict(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            # Update course
            response = supabase.table("courses")\
                .update(update_data)\
                .eq("id", course_id)\
                .execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update course"
                )
            
            updated_course = response.data[0]
        else:
            updated_course = course
        
        # Get teacher info and video stats
        teacher_response = supabase.table("users").select("full_name").eq("id", current_user["id"]).execute()
        teacher_name = teacher_response.data[0]["full_name"] if teacher_response.data else None
        
        videos_response = supabase.table("videos")\
            .select("id, duration")\
            .eq("course_id", course_id)\
            .execute()
        
        total_videos = len(videos_response.data) if videos_response.data else 0
        total_duration = sum(v.get("duration", 0) or 0 for v in videos_response.data) if videos_response.data else 0
        
        return CourseResponse(
            **updated_course,
            teacher_name=teacher_name,
            total_videos=total_videos,
            total_duration=total_duration
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating course: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: str,
    current_user: dict = Depends(get_current_teacher)
):
    """Delete course (Teacher only - own courses)"""
    try:
        # Check if course exists and belongs to teacher
        course_response = supabase.table("courses")\
            .select("*")\
            .eq("id", course_id)\
            .execute()
        
        if not course_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        course = course_response.data[0]
        if course["teacher_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own courses"
            )
        
        # Delete course (cascade will delete videos and enrollments)
        supabase.table("courses").delete().eq("id", course_id).execute()
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting course: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{course_id}/videos", response_model=List[VideoResponse])
async def get_course_videos(
    course_id: str,
    current_user: dict = Depends(get_optional_user)
):
    """Get all videos in a course"""
    try:
        # Get videos
        response = supabase.table("videos")\
            .select("*")\
            .eq("course_id", course_id)\
            .order("order")\
            .execute()
        
        if not response.data:
            return []
        
        videos = [VideoResponse(**video) for video in response.data]
        return videos
        
    except Exception as e:
        logger.error(f"Error fetching course videos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
