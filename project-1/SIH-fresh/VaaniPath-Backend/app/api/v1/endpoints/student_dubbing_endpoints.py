# Student-facing dubbing endpoints
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.api.deps import get_current_user

# These endpoints will be appended to processing.py

student_dubbing_endpoints = """
# ==========================================
# STUDENT ENDPOINTS (Content Dubbing)  
# ==========================================

@router.get("/content/{video_id}/{language}")
async def get_dubbed_content(
    video_id: str,
    language: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    '''
    🎬 **[STUDENT] Get Dubbed/Translated Content**
    
    Returns dubbed video/audio or translated document URL.
    Implements smart caching - returns existing URL if available, triggers generation if not.
    '''
    try:
        if not supabase:
            raise HTTPException(status_code=503, detail="Database not configured")
        
        # 1. Verify student is enrolled
        enrollment = supabase.table("enrollments").select("id").eq(
            "user_id", current_user["id"]
        ).eq("video_id", video_id).execute()
        
        if not enrollment.data:
            raise HTTPException(status_code=403, detail="Not enrolled in this course")
        
        # 2. Get video info to determine content type
        video_response = supabase.table("videos").select("content_type, file_url, title").eq(
            "id", video_id
        ).execute()
        
        if not video_response.data:
            raise HTTPException(status_code=404, detail="Content not found")
        
        video = video_response.data[0]
        content_type = video.get("content_type", "video")
        
        # 3. Check cache - look for existing translation
        translation_response = supabase.table("translations").select("*").eq(
            "video_id", video_id
        ).eq("language", language).execute()
        
        # 4. CACHING LOGIC - Return if already exists
        if translation_response.data:
            translation = translation_response.data[0]
            status_val = translation.get("status")
            
            # If completed, return cached URL
            if status_val == "completed":
                content_url = None
                if content_type == "video":
                    content_url = translation.get("dubbed_video_url")
                elif content_type == "audio":
                    content_url = translation.get("audio_url")
                elif content_type == "document":
                    content_url = translation.get("dubbed_video_url")  # Stored in same field
                
                if content_url:
                    return {
                        "video_id": video_id,
                        "language": language,
                        "content_type": content_type,
                        "content_url": content_url,
                        "status": "completed",
                        "cached": True,
                        "message": "Content already available"
                    }
            
            # If currently processing, return status
            if status_val in ["pending", "processing"]:
                return {
                    "video_id": video_id,
                    "language": language,
                    "content_type": content_type,
                    "status": "processing",
                    "cached": False,
                    "message": "Content is being generated. Please check back in a few minutes."
                }
            
            # If failed previously, retry
            if status_val == "failed":
                supabase.table("translations").update({
                    "status": "processing",
                    "error_message": None,
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("video_id", video_id).eq("language", language).execute()
                
                background_tasks.add_task(process_dubbing_task, video_id, language, content_type)
                
                return {
                    "video_id": video_id,
                    "language": language,
                    "content_type": content_type,
                    "status": "processing",
                    "cached": False,
                    "message": "Retrying content generation"
                }
        
        # 5. Not in cache - create new entry and trigger generation
        supabase.table("translations").insert({
            "video_id": video_id,
            "language": language,
            "translated_text": "", 
            "status": "processing",
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        # Trigger background dubbing with content type
        background_tasks.add_task(process_dubbing_task, video_id, language, content_type)
        
        return {
            "video_id": video_id,
            "language": language,
            "content_type": content_type,
            "status": "processing",
            "cached": False,
            "message": f"{content_type.capitalize()} dubbing/translation started. This may take 2-5 minutes."
        }
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Get dubbed content error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
"""

# Copy and append this to processing.py manually or via file edit
