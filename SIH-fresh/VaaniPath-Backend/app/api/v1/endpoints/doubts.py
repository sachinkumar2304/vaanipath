from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid
import logging
from app.api.deps import get_current_user, get_current_teacher
from app.db.supabase_client import supabase
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# --- Models ---
class DoubtBase(BaseModel):
    video_id: str
    question: str
    lecture_number: Optional[int] = 1
    subject: Optional[str] = "General"

class DoubtCreate(DoubtBase):
    pass

class DoubtAnswer(BaseModel):
    answer: str

class Doubt(DoubtBase):
    id: str
    user_id: str
    student_name: Optional[str] = None
    course_name: Optional[str] = None
    answer: Optional[str] = None
    status: str  # 'pending', 'answered'
    created_at: datetime
    answered_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Endpoints ---

@router.post("/", response_model=Doubt)
async def create_doubt(
    doubt: DoubtCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Student asks a doubt
    """
    try:
        # Check if Supabase is configured
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            # Mock response
            return {
                "id": str(uuid.uuid4()),
                "user_id": current_user["id"],
                "video_id": doubt.video_id,
                "question": doubt.question,
                "lecture_number": doubt.lecture_number,
                "subject": doubt.subject,
                "status": "pending",
                "created_at": datetime.utcnow(),
                "student_name": current_user.get("full_name", "Student")
            }

        # Verify video exists
        video_response = supabase.table("videos").select("title").eq("id", doubt.video_id).execute()
        if not video_response.data:
            raise HTTPException(status_code=404, detail="Video not found")
        
        video_title = video_response.data[0]["title"]

        doubt_data = {
            "user_id": current_user["id"],
            "video_id": doubt.video_id,
            "question": doubt.question,
            "lecture_number": doubt.lecture_number,
            "subject": doubt.subject,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }

        response = supabase.table("doubts").insert(doubt_data).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create doubt")
        
        created_doubt = response.data[0]
        created_doubt["student_name"] = current_user.get("full_name", "Student")
        created_doubt["course_name"] = video_title
        
        return created_doubt

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create doubt error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[Doubt])
async def get_student_doubts(
    current_user: dict = Depends(get_current_user)
):
    """
    Get doubts raised by the current student
    """
    try:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            return []

        user_id = current_user["id"]

        # Get student's doubts with video info
        doubts_response = supabase.table("doubts")\
            .select("*, videos(title)")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .execute()
        
        if not doubts_response.data:
            return []

        # Format response
        doubts = []
        for d in doubts_response.data:
            doubts.append({
                **d,
                "student_name": current_user.get("full_name", "You"),
                "course_name": d.get("videos", {}).get("title", "Unknown Course")
            })
            
        return doubts

    except Exception as e:
        logger.error(f"Get student doubts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/teacher", response_model=List[Doubt])

async def get_teacher_doubts(
    current_user: dict = Depends(get_current_teacher)
):
    """
    Get doubts for videos uploaded by the current teacher
    """
    try:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            return []

        teacher_id = current_user["id"]

        # 1. Get all video IDs uploaded by this teacher
        videos_response = supabase.table("videos").select("id, title").eq("uploaded_by", teacher_id).execute()
        
        if not videos_response.data:
            return []
        
        video_map = {v["id"]: v["title"] for v in videos_response.data}
        video_ids = list(video_map.keys())

        # 2. Get doubts for these videos
        # Use explicit relationship name to avoid ambiguity
        doubts_response = supabase.table("doubts")\
            .select("*, users!doubts_user_fk(full_name)")\
            .in_("video_id", video_ids)\
            .order("created_at", desc=True)\
            .execute()
        
        if not doubts_response.data:
            return []

        # 3. Format response
        doubts = []
        for d in doubts_response.data:
            doubts.append({
                **d,
                "student_name": d.get("users", {}).get("full_name", "Unknown Student"),
                "course_name": video_map.get(d["video_id"], "Unknown Course")
            })
            
        return doubts

    except Exception as e:
        logger.error(f"Get teacher doubts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{doubt_id}/answer", response_model=Doubt)
async def answer_doubt(
    doubt_id: str,
    answer_data: DoubtAnswer,
    current_user: dict = Depends(get_current_teacher)
):
    """
    Teacher answers a doubt
    """
    try:
        # Verify doubt exists and belongs to teacher's video
        doubt_response = supabase.table("doubts").select("*, videos(uploaded_by)").eq("id", doubt_id).execute()
        
        if not doubt_response.data:
            raise HTTPException(status_code=404, detail="Doubt not found")
        
        doubt = doubt_response.data[0]
        
        # Check permission
        if doubt.get("videos", {}).get("uploaded_by") != current_user["id"]:
            # Allow admin override, but for now restrict to owner
            if not current_user.get("is_admin"):
                raise HTTPException(status_code=403, detail="Not authorized to answer this doubt")

        # Update doubt
        update_data = {
            "answer": answer_data.answer,
            "status": "answered",
            "answered_at": datetime.utcnow().isoformat()
        }

        response = supabase.table("doubts").update(update_data).eq("id", doubt_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to update doubt")
        
        updated_doubt = response.data[0]
        
        # Fetch extra info for response
        user_response = supabase.table("users").select("full_name").eq("id", updated_doubt["user_id"]).execute()
        video_response = supabase.table("videos").select("title").eq("id", updated_doubt["video_id"]).execute()
        
        updated_doubt["student_name"] = user_response.data[0]["full_name"] if user_response.data else "Unknown"
        updated_doubt["course_name"] = video_response.data[0]["title"] if video_response.data else "Unknown"
        
        return updated_doubt

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Answer doubt error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
