"""
Community Routes
API endpoints for community management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from uuid import UUID
from app.features.community.models.community import (
    CommunityCreate, CommunityUpdate, CommunityResponse, CommunityList
)
from app.features.community.services.community_service import CommunityService
from app.api.deps import get_current_user, get_current_teacher
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/communities", tags=["Communities"])


@router.post("", response_model=CommunityResponse, status_code=status.HTTP_201_CREATED)
async def create_community(
    community_data: CommunityCreate,
    current_user: dict = Depends(get_current_teacher)  # Only teachers can create
):
    """Create a new community (Teachers only)"""
    try:
        return await CommunityService.create_community(
            community_data,
            UUID(current_user["id"])
        )
    except Exception as e:
        logger.error(f"Error creating community: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("", response_model=CommunityList)
async def get_communities(
    page: int = 1,
    page_size: int = 20,
    domain: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get list of communities"""
    try:
        return await CommunityService.get_communities(
            page=page,
            page_size=page_size,
            domain=domain,
            user_id=UUID(current_user["id"])
        )
    except Exception as e:
        logger.error(f"Error fetching communities: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{community_id}", response_model=CommunityResponse)
async def get_community(
    community_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Get community by ID"""
    try:
        return await CommunityService.get_community(
            community_id,
            UUID(current_user["id"])
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error fetching community: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{community_id}/join")
async def join_community(
    community_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Join a community"""
    try:
        return await CommunityService.join_community(
            community_id,
            UUID(current_user["id"])
        )
    except Exception as e:
        logger.error(f"Error joining community: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{community_id}/leave")
async def leave_community(
    community_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Leave a community"""
    try:
        return await CommunityService.leave_community(
            community_id,
            UUID(current_user["id"])
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error leaving community: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
