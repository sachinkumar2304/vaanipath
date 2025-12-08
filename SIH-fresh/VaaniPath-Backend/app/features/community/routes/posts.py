"""
Post Routes
API endpoints for posts, likes, and replies
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import Optional
from uuid import UUID
import logging
import uuid
import cloudinary
import cloudinary.uploader
from app.config import settings
from app.features.community.models.post import (
    PostCreate, PostUpdate, PostResponse, PostList,
    ReplyCreate, ReplyResponse, ReplyList
)
from app.features.community.services.post_service import PostService
from app.api.deps import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.post("/upload-media", status_code=status.HTTP_201_CREATED)
async def upload_media(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload media for a post
    """
    try:
        # Validate file format
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        file_ext = file.filename.split('.')[-1].lower()
        if file_ext not in ["jpg", "jpeg", "png", "webp", "gif"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file format. Allowed: jpg, jpeg, png, webp, gif"
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
            public_id=f"community/posts/{temp_id}",
            folder="gyanify/community/posts",
            overwrite=True,
            tags=["gyanify", "community", "post"]
        )
        
        return {"url": upload_result.get("secure_url")}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading media: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new post"""
    try:
        return await PostService.create_post(
            post_data,
            UUID(current_user["id"]),
            current_user
        )
    except Exception as e:
        logger.error(f"Error creating post: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("", response_model=PostList)
async def get_posts(
    community_id: UUID,
    page: int = 1,
    page_size: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Get posts for a community"""
    try:
        return await PostService.get_posts(
            community_id,
            page=page,
            page_size=page_size,
            user_id=UUID(current_user["id"])
        )
    except Exception as e:
        logger.error(f"Error fetching posts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{post_id}/like")
async def toggle_like(
    post_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Like or unlike a post"""
    try:
        return await PostService.toggle_like(
            post_id,
            UUID(current_user["id"])
        )
    except Exception as e:
        logger.error(f"Error toggling like: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{post_id}/reply", response_model=ReplyResponse, status_code=status.HTTP_201_CREATED)
async def create_reply(
    post_id: UUID,
    reply_data: ReplyCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a reply to a post"""
    try:
        # Ensure post_id matches
        reply_data.post_id = post_id
        return await PostService.create_reply(
            reply_data,
            UUID(current_user["id"]),
            current_user
        )
    except Exception as e:
        logger.error(f"Error creating reply: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{post_id}/replies", response_model=ReplyList)
async def get_replies(
    post_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Get replies for a post"""
    try:
        return await PostService.get_replies(
            post_id,
            UUID(current_user["id"])
        )
    except Exception as e:
        logger.error(f"Error fetching replies: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
