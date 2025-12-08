from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import logging
from app.api.deps import get_current_user, get_current_teacher
from app.db.supabase_client import supabase
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# Models
class QuizOption(BaseModel):
    text: str
    is_correct: bool

class QuizQuestion(BaseModel):
    id: str
    video_id: str
    question_text: str
    question_type: str
    options: Optional[List[dict]] = None
    correct_answer: str
    difficulty: Optional[str] = None
    timestamp: Optional[float] = None

class QuizAnswer(BaseModel):
    question_id: str
    user_answer: str

class QuizSubmission(BaseModel):
    answers: List[QuizAnswer]

class QuizResult(BaseModel):
    total_questions: int
    correct_answers: int
    score_percentage: float
    passed: bool

@router.get("/video/{video_id}", response_model=List[QuizQuestion])
async def get_video_quiz(
    video_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get quiz questions for a video (only if student has completed it)
    """
    try:
        if not supabase:
            raise HTTPException(status_code=503, detail="Database not configured")
        
        # Check if student is enrolled and has completed the video
        enrollment = supabase.table("enrollments").select("progress_percentage").eq(
            "user_id", current_user["id"]
        ).eq("video_id", video_id).execute()
        
        if not enrollment.data:
            raise HTTPException(status_code=403, detail="Not enrolled in this course")
        
        # Only show quiz if progress >= 90% (nearly completed)
        if enrollment.data[0].get("progress_percentage", 0) < 90:
            return []
        
        # Get quiz questions
        questions_response = supabase.table("quiz_questions").select("*").eq(
            "video_id", video_id
        ).execute()
        
        if not questions_response.data:
            return []
        
        return questions_response.data
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get quiz error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/video/{video_id}/submit", response_model=QuizResult)
async def submit_quiz(
    video_id: str,
    submission: QuizSubmission,
    current_user: dict = Depends(get_current_user)
):
    """
    Submit quiz answers and get results
    """
    try:
        if not supabase:
            raise HTTPException(status_code=503, detail="Database not configured")
        
        # Get all questions for this video
        questions_response = supabase.table("quiz_questions").select("*").eq(
            "video_id", video_id
        ).execute()
        
        if not questions_response.data:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        questions = {q["id"]: q for q in questions_response.data}
        total_questions = len(questions)
        correct_answers = 0
        
        # Check each answer
        for answer in submission.answers:
            question = questions.get(answer.question_id)
            if question and question["correct_answer"] == answer.user_answer:
                correct_answers += 1
            
            # Save answer to database
            supabase.table("quiz_responses").insert({
                "user_id": current_user["id"],
                "question_id": answer.question_id,
                "user_answer": answer.user_answer,
                "is_correct": question["correct_answer"] == answer.user_answer if question else False
            }).execute()
        
        score_percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        passed = score_percentage >= 60  # 60% passing threshold
        
        # Award GyanPoints if passed
        if passed:
            try:
                from app.features.community.services.gyan_points_service import GyanPointsService
                # Check if points already awarded for this video quiz
                # We can check transaction history or use a specific DB constraint. 
                # For simplicity, checking existing transaction for this video_id in description or reference logic would be ideal if reference_id supported string (video_id is string?).
                # Since reference_id is UUID in service, and video_id is string/uuid?, let's check carefully.
                # Assuming video_id is a UUID string.
                
                # Check directly in transactions table if we can't trust service wrapper for uniqueness check
                # But let's try to be clean.
                
                # Verify if we already gave points for this video_id
                history = await GyanPointsService.get_history(current_user["id"])
                already_awarded = any(
                    t['transaction_type'] == 'course_quiz_reward' and 
                    t['description'].endswith(f"Video {video_id}") 
                    for t in history
                )
                
                if not already_awarded:
                    await GyanPointsService.add_points(
                        user_id=current_user["id"],
                        points=50,
                        source="course_quiz_reward",
                        description=f"Quiz Completion Reward: Video {video_id}",
                        reference_id=None # video_id might not be UUID, safe to leave None or try convert if sure.
                    )
            except Exception as e:
                logger.error(f"Failed to award quiz points: {e}")

        return {
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "score_percentage": score_percentage,
            "passed": passed
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Submit quiz error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
