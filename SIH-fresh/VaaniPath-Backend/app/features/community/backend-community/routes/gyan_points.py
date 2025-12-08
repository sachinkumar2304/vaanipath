from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from pydantic import BaseModel
from app.features.community.services.gyan_points_service import GyanPointsService
from app.api.deps import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/gyan-points", tags=["GyanPoints"])

class PointResponse(BaseModel):
    total_points: int

class TransactionHistory(BaseModel):
    id: UUID
    points_change: int
    transaction_type: str
    description: str
    created_at: str

@router.get("/me", response_model=PointResponse)
async def get_my_points(
    current_user: dict = Depends(get_current_user)
):
    """Get current user's total GyanPoints"""
    try:
        points = await GyanPointsService.get_user_points(UUID(current_user["id"]))
        return PointResponse(total_points=points)
    except Exception as e:
        logger.error(f"Error fetching points: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/history", response_model=List[TransactionHistory])
async def get_my_history(
    current_user: dict = Depends(get_current_user)
):
    """Get point transaction history"""
    try:
        return await GyanPointsService.get_history(UUID(current_user["id"]))
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
