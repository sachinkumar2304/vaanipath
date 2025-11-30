from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional, Dict
from app.models.review import (
    ReviewCreate,
    ReviewResponse,
    PendingReview,
    ReviewStats
)
from app.api.deps import get_current_admin, get_current_user
from app.db.supabase_client import supabase
from app.config import settings
from datetime import datetime
import logging
import uuid

router = APIRouter()
logger = logging.getLogger(__name__)


class ReviewSubmission(BaseModel):
    """Review submission model"""
    translation_id: str
    approved: bool
    feedback: Optional[str] = None
    corrections: Optional[dict] = None


class ReviewItem(BaseModel):
    """Item pending review"""
    id: str
    video_id: str
    language: str
    original_text: str
    translated_text: str
    timestamp: Optional[float] = None
    quality_score: float


@router.get("/pending", response_model=List[PendingReview])
async def get_pending_reviews(
    limit: int = 20,
    current_user: dict = Depends(get_current_admin)
):
    """
    Get all translations pending review
    Returns translations that need human review before publishing
    """
    try:
        # Check if Supabase is configured
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            logger.warning("Supabase not configured, returning mock reviews")
            return [
                {
                    "id": str(uuid.uuid4()),
                    "video_id": str(uuid.uuid4()),
                    "video_title": "Introduction to Python Programming",
                    "language": "hi",
                    "transcript_url": "https://example.com/transcript.txt",
                    "translated_text_url": "https://example.com/translated.txt",
                    "audio_url": "https://example.com/audio.mp3",
                    "video_url": None,
                    "quality_score": 85.5,
                    "created_at": datetime.utcnow().isoformat()
                },
                {
                    "id": str(uuid.uuid4()),
                    "video_id": str(uuid.uuid4()),
                    "video_title": "Advanced Mathematics - Calculus",
                    "language": "ta",
                    "transcript_url": "https://example.com/transcript2.txt",
                    "translated_text_url": "https://example.com/translated2.txt",
                    "audio_url": "https://example.com/audio2.mp3",
                    "video_url": None,
                    "quality_score": 78.3,
                    "created_at": datetime.utcnow().isoformat()
                }
            ]
        
        # Get translations with status 'review_pending'
        translations_response = supabase.table("translations")\
            .select("*, videos(title)")\
            .eq("status", "review_pending")\
            .limit(limit)\
            .execute()
        
        if not translations_response.data:
            return []
        
        pending_reviews = []
        for translation in translations_response.data:
            pending_reviews.append({
                "id": translation["id"],
                "video_id": translation["video_id"],
                "video_title": translation.get("videos", {}).get("title", "Unknown"),
                "language": translation["language"],
                "transcript_url": translation.get("transcript_url"),
                "translated_text_url": translation.get("translated_text_url"),
                "audio_url": translation.get("audio_url"),
                "video_url": translation.get("video_url"),
                "quality_score": translation.get("quality_score", 0),
                "created_at": translation["created_at"]
            })
        
        return pending_reviews
    
    except Exception as e:
        logger.error(f"Get pending reviews error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/submit", response_model=ReviewResponse)
async def submit_review(
    review: ReviewCreate,
    current_user: dict = Depends(get_current_admin)
):
    """
    Submit review for a translation
    If approved: Mark translation as completed
    If not approved: Keep in review_pending and use corrections for reprocessing
    """
    try:
        # Check if Supabase is configured
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            logger.warning("Supabase not configured, returning mock response")
            return {
                "id": str(uuid.uuid4()),
                "translation_id": review.translation_id,
                "reviewer_id": current_user.get("id", "admin"),
                "approved": review.approved,
                "feedback": review.feedback,
                "corrections": review.corrections,
                "reviewed_at": datetime.utcnow().isoformat()
            }
        
        # Verify translation exists
        translation_response = supabase.table("translations")\
            .select("*")\
            .eq("id", review.translation_id)\
            .execute()
        
        if not translation_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Translation not found"
            )
        
        # Create review record
        review_data = {
            "translation_id": review.translation_id,
            "reviewer_id": current_user["id"],
            "approved": review.approved,
            "feedback": review.feedback,
            "corrections": review.corrections,
            "reviewed_at": datetime.utcnow().isoformat()
        }
        
        review_response = supabase.table("reviews").insert(review_data).execute()
        
        if not review_response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to submit review"
            )
        
        # Update translation status
        new_status = "completed" if review.approved else "needs_revision"
        
        supabase.table("translations")\
            .update({"status": new_status, "updated_at": datetime.utcnow().isoformat()})\
            .eq("id", review.translation_id)\
            .execute()
        
        # If approved, update video status
        if review.approved:
            # Check if all translations for this video are completed
            translation = translation_response.data[0]
            video_id = translation["video_id"]
            
            all_translations = supabase.table("translations")\
                .select("status")\
                .eq("video_id", video_id)\
                .execute()
            
            if all_translations.data:
                all_completed = all(t["status"] == "completed" for t in all_translations.data)
                
                if all_completed:
                    supabase.table("videos")\
                        .update({"status": "completed"})\
                        .eq("id", video_id)\
                        .execute()
        
        # TODO: If not approved, trigger reprocessing with corrections
        # from app.workers.tasks import reprocess_translation
        # reprocess_translation.delay(review.translation_id, review.corrections)
        
        return review_response.data[0]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Submit review error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{translation_id}/history", response_model=List[ReviewResponse])
async def get_review_history(
    translation_id: str,
    current_user: dict = Depends(get_current_admin)
):
    """
    Get review history for a translation
    Shows all review attempts and feedback
    """
    try:
        # Check if Supabase is configured
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            logger.warning("Supabase not configured, returning mock history")
            return [
                {
                    "id": str(uuid.uuid4()),
                    "translation_id": translation_id,
                    "reviewer_id": "admin-1",
                    "approved": False,
                    "feedback": "Some terms need correction",
                    "corrections": {"00:30": "Corrected text here"},
                    "reviewed_at": "2025-11-17T10:00:00Z"
                },
                {
                    "id": str(uuid.uuid4()),
                    "translation_id": translation_id,
                    "reviewer_id": "admin-1",
                    "approved": True,
                    "feedback": "Looks good now!",
                    "corrections": None,
                    "reviewed_at": "2025-11-17T14:00:00Z"
                }
            ]
        
        # Get all reviews for this translation
        response = supabase.table("reviews")\
            .select("*")\
            .eq("translation_id", translation_id)\
            .order("reviewed_at", desc=True)\
            .execute()
        
        if not response.data:
            return []
        
        return response.data
    
    except Exception as e:
        logger.error(f"Get review history error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/stats", response_model=ReviewStats)
async def get_review_stats(
    current_user: dict = Depends(get_current_admin)
):
    """
    Get review statistics
    Shows overview of pending, approved, and rejected reviews
    """
    try:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            return {
                "total_pending": 5,
                "total_approved": 42,
                "total_rejected": 8,
                "avg_review_time_hours": 2.5
            }
        
        # Count pending reviews
        pending_response = supabase.table("translations")\
            .select("*")\
            .eq("status", "review_pending")\
            .execute()
        
        # Count approved reviews
        approved_response = supabase.table("reviews")\
            .select("*")\
            .eq("approved", True)\
            .execute()
        
        # Count rejected reviews
        rejected_response = supabase.table("reviews")\
            .select("*")\
            .eq("approved", False)\
            .execute()
        
        # Calculate average review time (simplified)
        avg_time = 2.5  # TODO: Calculate from actual data
        
        return {
            "total_pending": len(pending_response.data) if pending_response.data else 0,
            "total_approved": len(approved_response.data) if approved_response.data else 0,
            "total_rejected": len(rejected_response.data) if rejected_response.data else 0,
            "avg_review_time_hours": avg_time
        }
    
    except Exception as e:
        logger.error(f"Get review stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{review_id}")
async def delete_review(
    review_id: str,
    current_user: dict = Depends(get_current_admin)
):
    """
    Delete a review record (Admin only)
    """
    try:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            return {"message": "Review deleted (mock)"}
        
        response = supabase.table("reviews").delete().eq("id", review_id).execute()
        
        return {"message": "Review deleted successfully"}
    
    except Exception as e:
        logger.error(f"Delete review error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
