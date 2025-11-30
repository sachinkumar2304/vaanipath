from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from app.models.video import VideoUpload, VideoResponse, VideoProgress, VideoList, DomainType, WatchProgress
from app.api.deps import get_current_admin, get_current_user, get_current_teacher, get_optional_user
from app.db.supabase_client import supabase
from app.config import settings
import logging
import uuid
import cloudinary
import cloudinary.uploader
from datetime import datetime
from fastapi import BackgroundTasks
from app.services.ml_localizer_client import trigger_transcription_with_content

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_video(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    domain: str = Form(...),
    source_language: str = Form("en"),
    target_languages: str = Form(...),  # Comma-separated
    course_id: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: dict = Depends(get_current_teacher)
):
    """
    Upload a video for processing (Admin or Teacher)
    """
    try:
        # Validate file format
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        file_ext = file.filename.split('.')[-1].lower()
        
        # Determine content type and resource type
        content_type = "video"
        resource_type = "video"
        
        if file_ext in settings.video_formats_list:
            content_type = "video"
            resource_type = "video"
        elif file_ext in settings.audio_formats_list:
            content_type = "audio"
            resource_type = "video"  # Cloudinary treats audio as video resource_type usually, or 'auto'
        elif file_ext in settings.document_formats_list:
            content_type = "document"
            resource_type = "raw"  # Documents are 'raw' or 'image' depending on type
        else:
            allowed = settings.video_formats_list + settings.audio_formats_list + settings.document_formats_list
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file format. Allowed: {', '.join(allowed)}"
            )
        
        # Generate temp ID for Cloudinary path (will use actual video_id from DB response)
        temp_video_id = str(uuid.uuid4())
        
        # Configure Cloudinary
        if not settings.CLOUDINARY_CLOUD_NAME or not settings.CLOUDINARY_API_KEY:
            logger.error("Cloudinary credentials not configured")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Storage service not configured"
            )
        
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET
        )
        
        # Read file content
        file_content = await file.read()
        
        # Upload to Cloudinary
        logger.info(f"Uploading {content_type} to Cloudinary...")
        try:
            # For raw files (documents), we MUST keep the extension in the public_id
            # otherwise Cloudinary won't serve it with the correct extension/MIME type
            public_id_name = file.filename.split('.')[0]
            if resource_type == "raw":
                public_id_name = file.filename
                
            upload_result = cloudinary.uploader.upload(
                file_content,
                resource_type=resource_type,
                public_id=f"videos/{temp_video_id}/{public_id_name}",
                folder="gyanify/videos",
                overwrite=True,
                tags=["gyanify", content_type, domain, source_language]
            )
            
            if "error" in upload_result:
                logger.error(f"Cloudinary error: {upload_result['error']}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cloudinary upload error: {upload_result['error'].get('message', 'Unknown error')}"
                )
            
            cloudinary_url = upload_result.get("secure_url", upload_result.get("url"))
            logger.info(f"{content_type.capitalize()} uploaded successfully: {cloudinary_url}")
        except Exception as upload_error:
            logger.error(f"Cloudinary upload failed: {upload_error}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported format or file: {str(upload_error)}"
            )
        
        # Prepare video data for database - let Supabase generate ID
        video_data = {
            "title": title,
            "description": description or "",
            "domain": domain,
            "source_language": source_language,
            "target_languages": target_languages.split(","),
            "status": "uploaded",
            "file_url": cloudinary_url,
            "cloudinary_public_id": upload_result.get("public_id"),
            "thumbnail_url": upload_result.get("thumbnail_url"),
            "duration": upload_result.get("duration", 0),
            "uploaded_by": current_user.get("id", "admin"),
            "content_type": content_type,  # video, audio, or document
            "course_id": course_id
        }
        
        # Save to database (REQUIRED - not optional)
        if not supabase:
            logger.error("Supabase not initialized")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database service unavailable"
            )
        
        try:
            db_response = supabase.table("videos").insert(video_data).execute()
            
            if not db_response.data:
                logger.error("Failed to insert video - no data returned")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to save video metadata"
                )
            
            saved_video = db_response.data[0]
            logger.info(f"Video metadata saved to database: {saved_video.get('id')}")
            
            # ML Transcription/Dubbing will be triggered on-demand when student selects a language
            # This saves upload time and only processes languages that are actually requested
            
            return saved_video
        except HTTPException:
            raise
        except Exception as db_error:
            logger.error(f"Failed to save video metadata: {db_error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save video metadata: {str(db_error)}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.get("/", response_model=VideoList)
async def list_videos(
    page: int = 1,
    page_size: int = 20,
    domain: Optional[str] = None,
    video_status: Optional[str] = None,
    enrolled: Optional[bool] = None,
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """
    List all videos (with pagination and filters)
    """
    try:
        # Check if Supabase is configured
        if not supabase or not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            logger.error("❌ Supabase not configured")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database service unavailable"
            )
        
        offset = (page - 1) * page_size
        
        # Build query with count
        query = supabase.table("videos").select("*", count="exact")
        
        # Apply filters
        if domain:
            query = query.eq("domain", domain)
        
        if video_status:
            query = query.eq("status", video_status)
        
        # Filter by enrolled (if user is logged in)
        if enrolled is not None and current_user:
            if enrolled:
                # Get user's enrolled videos
                enrollments = supabase.table("enrollments")\
                    .select("video_id")\
                    .eq("user_id", current_user["id"])\
                    .execute()
                
                video_ids = [e["video_id"] for e in enrollments.data]
                if video_ids:
                    query = query.in_("id", video_ids)
                else:
                    # No enrollments, return empty
                    return {
                        "videos": [],
                        "total": 0,
                        "page": page,
                        "page_size": page_size
                    }
        
        # Apply pagination and execute
        response = query.range(offset, offset + page_size - 1).execute()
        
        return {
            "videos": response.data or [],
            "total": response.count or 0,
            "page": page,
            "page_size": page_size
        }
    
    except Exception as e:
        logger.error(f"List videos error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/my-videos")
async def get_my_videos(
    page: int = 1,
    page_size: int = 20,
    current_user: dict = Depends(get_current_teacher)
):
    """
    Get all videos uploaded by the current teacher
    """
    try:
        if not supabase or not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            logger.error("❌ Supabase not configured")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database service unavailable"
            )
            
        offset = (page - 1) * page_size
        
        # Get videos uploaded by this teacher
        response = supabase.table("videos")\
            .select("*", count="exact")\
            .eq("uploaded_by", current_user["id"])\
            .range(offset, offset + page_size - 1)\
            .execute()
            
        return {
            "videos": response.data or [],
            "total": response.count or 0,
            "page": page,
            "page_size": page_size
        }

    except Exception as e:
        logger.error(f"Get my videos error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get video details
    """
    try:
        response = supabase.table("videos").select("*").eq("id", video_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found"
            )
            
        video = response.data[0]
        
        # Increment view count
        # Note: In a high-concurrency environment, use an RPC function or atomic increment
        try:
            current_views = video.get("views", 0) or 0
            new_views = current_views + 1
            supabase.table("videos").update({"views": new_views}).eq("id", video_id).execute()
            video["views"] = new_views
        except Exception as e:
            logger.warning(f"Failed to increment views for video {video_id}: {e}")
            
        return video
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get video error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{video_id}/view", status_code=status.HTTP_200_OK)
async def increment_view(
    video_id: str,
    current_user: dict = Depends(get_optional_user)
):
    """
    Increment view count for a video
    """
    try:
        # Get current views
        response = supabase.table("videos").select("views").eq("id", video_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found"
            )
            
        current_views = response.data[0].get("views", 0) or 0
        
        # Increment
        supabase.table("videos").update({"views": current_views + 1}).eq("id", video_id).execute()
        
        return {"message": "View counted", "views": current_views + 1}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Increment view error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_video(
    video_id: str,
    current_user: dict = Depends(get_current_teacher)
):
    """
    Delete a video (Admin or Owner Teacher)
    """
    try:
        # Check if video exists and user has permission
        video = supabase.table("videos").select("*").eq("id", video_id).execute()
        
        if not video.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found"
            )
            
        video_data = video.data[0]
        
        # Check permission: Admin or Owner
        if not current_user.get("is_admin") and video_data.get("uploaded_by") != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this video"
            )
            
        # Delete from Cloudinary
        if video_data.get("cloudinary_public_id"):
            try:
                cloudinary.uploader.destroy(video_data["cloudinary_public_id"], resource_type="video")
            except Exception as e:
                logger.error(f"Failed to delete from Cloudinary: {e}")
                # Continue to delete from DB even if Cloudinary fails
        
        # Delete from DB
        supabase.table("videos").delete().eq("id", video_id).execute()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete video error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{video_id}/enroll")
async def enroll_video(
    video_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Enroll in a video course
    """
    try:
        # Check if video exists
        video = supabase.table("videos").select("id").eq("id", video_id).execute()
        if not video.data:
            raise HTTPException(status_code=404, detail="Video not found")

        # Check if already enrolled
        existing = supabase.table("enrollments").select("id").eq("user_id", current_user["id"]).eq("video_id", video_id).execute()
        if existing.data:
            return {"message": "Already enrolled"}

        # Enroll
        enrollment_data = {
            "user_id": current_user["id"],
            "video_id": video_id,
            "enrolled_at": datetime.utcnow().isoformat(),
            "progress_percentage": 0
        }
        
        supabase.table("enrollments").insert(enrollment_data).execute()
        return {"message": "Enrolled successfully"}
        
    except Exception as e:
        logger.error(f"Enrollment error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{video_id}/progress")
async def update_progress(
    video_id: str,
    progress_data: WatchProgress,
    current_user: dict = Depends(get_current_user)
):
    """
    Update video watch progress
    """
    try:
        # Update progress in enrollments table
        result = supabase.table("enrollments").update({
            "progress_percentage": progress_data.progress_percentage
        }).eq("user_id", current_user["id"]).eq("video_id", video_id).execute()
        
        if not result.data:
            # Try to enroll if not enrolled (auto-enroll on watch)
            enrollment_data = {
                "user_id": current_user["id"],
                "video_id": video_id,
                "enrolled_at": datetime.utcnow().isoformat(),
                "progress_percentage": progress_data.progress_percentage
            }
            supabase.table("enrollments").insert(enrollment_data).execute()
            
        return {"message": "Progress updated"}
        
    except Exception as e:
        logger.error(f"Progress update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{video_id}/progress")
async def get_progress(
    video_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get video watch progress
    """
    try:
        result = supabase.table("enrollments").select("progress_percentage").eq(
            "user_id", current_user["id"]
        ).eq("video_id", video_id).execute()
        
        if not result.data:
            return {"progress": 0}
            
        return {"progress": result.data[0].get("progress_percentage", 0)}
        
    except Exception as e:
        logger.error(f"Get progress error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{video_id}/available-languages")
async def get_video_available_languages(video_id: str):
    """Get all available dubbed languages for a video"""
    try:
        # Get all completed translations for this video
        response = supabase.table("translations")\
            .select("language, dubbed_video_url")\
            .eq("video_id", video_id)\
            .eq("status", "completed")\
            .execute()
            
        available_languages = []
        if response.data:
            for item in response.data:
                if item.get("dubbed_video_url"):
                    available_languages.append(item["language"])
        
        return {
            "video_id": video_id,
            "available_languages": available_languages
        }
    except Exception as e:
        logger.error(f"Error getting available languages: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{video_id}/dubbed/{language}")
async def check_dubbed_video(video_id: str, language: str):
    """Check if a dubbed version exists for a video"""
    try:
        # Check translations table
        response = supabase.table("translations")\
            .select("*")\
            .eq("video_id", video_id)\
            .eq("language", language)\
            .eq("status", "completed")\
            .execute()
            
        if response.data:
            # Return dubbed_video_url (this is where ML service saves the Cloudinary URL)
            dubbed_url = response.data[0].get("dubbed_video_url")
            if dubbed_url:
                return {"url": dubbed_url}
            
        raise HTTPException(status_code=404, detail="Dubbed version not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking dubbed video: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class DubbedVideoCreate(BaseModel):
    video_id: str
    language: str
    file_url: str
    duration: Optional[float] = None

@router.post("/dubbed", status_code=status.HTTP_201_CREATED)
async def save_dubbed_video(
    dubbed_video: DubbedVideoCreate,
    current_user: dict = Depends(get_current_user)
):
    """Save a dubbed video URL"""
    try:
        # Check if already exists
        existing = supabase.table("translations")\
            .select("id")\
            .eq("video_id", dubbed_video.video_id)\
            .eq("language", dubbed_video.language)\
            .execute()
            
        data = {
            "video_id": dubbed_video.video_id,
            "language": dubbed_video.language,
            "file_url": dubbed_video.file_url,
            "status": "completed",
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if existing.data:
            response = supabase.table("translations")\
                .update(data)\
                .eq("id", existing.data[0]["id"])\
                .execute()
        else:
            data["id"] = str(uuid.uuid4())
            data["created_at"] = datetime.utcnow().isoformat()
            response = supabase.table("translations").insert(data).execute()
            
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error saving dubbed video: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-thumbnail", status_code=status.HTTP_201_CREATED)
async def upload_thumbnail(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_teacher)
):
    """
    Upload a course thumbnail
    """
    try:
        # Validate file format
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        file_ext = file.filename.split('.')[-1].lower()
        if file_ext not in ["jpg", "jpeg", "png", "webp"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file format. Allowed: jpg, jpeg, png, webp"
            )
        
        # Configure Cloudinary
        if not settings.CLOUDINARY_CLOUD_NAME or not settings.CLOUDINARY_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Storage service not configured"
            )
        
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET
        )
        
        # Read file content
        file_content = await file.read()
        
        # Upload to Cloudinary
        temp_id = str(uuid.uuid4())
        upload_result = cloudinary.uploader.upload(
            file_content,
            resource_type="image",
            public_id=f"thumbnails/{temp_id}",
            folder="gyanify/thumbnails",
            overwrite=True,
            tags=["gyanify", "thumbnail"]
        )
        
        return {"thumbnail_url": upload_result.get("secure_url")}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading thumbnail: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
