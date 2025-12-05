"""
Competition Routes
API endpoints for competitions, quizzes, and leaderboards
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from app.features.community.models.competition import (
    CompetitionCreate, CompetitionUpdate, CompetitionResponse, CompetitionList,
    QuestionCreate, QuestionResponse, SubmissionCreate, SubmissionResponse,
    Leaderboard
)
from app.features.community.services.competition_service import CompetitionService
from app.core.deps import get_current_user, get_current_teacher
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/competitions", tags=["Competitions"])


@router.post("", response_model=CompetitionResponse, status_code=status.HTTP_201_CREATED)
async def create_competition(
    comp_data: CompetitionCreate,
    current_user: dict = Depends(get_current_teacher)  # Only teachers
):
    """Create a new competition (Teachers only)"""
    try:
        return await CompetitionService.create_competition(
            comp_data,
            UUID(current_user["id"])
        )
    except Exception as e:
        logger.error(f"Error creating competition: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{competition_id}/questions", response_model=List[QuestionResponse])
async def add_questions(
    competition_id: UUID,
    questions: List[QuestionCreate],
    current_user: dict = Depends(get_current_teacher)
):
    """Add questions to a competition (Creator only)"""
    try:
        return await CompetitionService.add_questions(
            competition_id,
            questions,
            UUID(current_user["id"])
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error adding questions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{competition_id}/register")
async def register_for_competition(
    competition_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Register for a competition"""
    try:
        return await CompetitionService.register_for_competition(
            competition_id,
            UUID(current_user["id"])
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error registering for competition: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{competition_id}/submit", response_model=SubmissionResponse)
async def submit_answer(
    competition_id: UUID,
    submission: SubmissionCreate,
    current_user: dict = Depends(get_current_user)
):
    """Submit an answer to a competition question"""
    try:
        # Ensure competition_id matches
        submission.competition_id = competition_id
        return await CompetitionService.submit_answer(
            submission,
            UUID(current_user["id"])
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error submitting answer: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{competition_id}/leaderboard", response_model=Leaderboard)
async def get_leaderboard(
    competition_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Get competition leaderboard"""
    try:
        return await CompetitionService.get_leaderboard(competition_id)
    except Exception as e:
        logger.error(f"Error fetching leaderboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
