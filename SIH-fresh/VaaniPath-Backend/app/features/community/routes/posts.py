"""
Post Routes
API endpoints for posts, likes, and replies
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from uuid import UUID
from app.features.community.models.post import (
    PostCreate, PostUpdate, PostResponse, PostList,
    ReplyCreate, ReplyResponse, ReplyList
)
from app.features.community.services.post_service import PostService
from app.core.deps import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/posts", tags=["Posts"])


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
