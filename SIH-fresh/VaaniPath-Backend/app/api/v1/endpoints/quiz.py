from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from app.models.quiz import (
    QuizQuestionResponse,
    QuizQuestionCreate,
    UserAnswer,
    AnswerResult,
    QuizSession,
    QuizResult,
    QuestionType,
    QuestionDifficulty
)
from pydantic import BaseModel
from app.api.deps import get_current_user, get_current_admin, get_current_teacher
from app.db.supabase_client import supabase
from app.config import settings
from datetime import datetime
import logging
import uuid

router = APIRouter()
logger = logging.getLogger(__name__)

# --- New Models for Teacher Quiz Creation ---
class QuestionCreate(BaseModel):
    question: str
    options: List[str]
    correctAnswer: int
    points: int

class QuizCreate(BaseModel):
    courseId: str  # This maps to video_id
    title: str
    description: str
    questions: List[QuestionCreate]

# --------------------------------------------

@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_quiz(
    quiz_data: QuizCreate,
    current_user: dict = Depends(get_current_teacher)
):
    """
    Teacher creates a quiz for a video (course)
    Replaces existing questions for that video
    """
    try:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            return {"message": "Quiz created (mock)", "quiz": quiz_data}

        video_id = quiz_data.courseId
        
        # Verify video belongs to teacher
        video_response = supabase.table("videos").select("uploaded_by").eq("id", video_id).execute()
        if not video_response.data:
            raise HTTPException(status_code=404, detail="Video/Course not found")
        
        if video_response.data[0]["uploaded_by"] != current_user["id"] and not current_user.get("is_admin"):
             raise HTTPException(status_code=403, detail="Not authorized to create quiz for this content")

        # Delete existing questions for this video (Replace mode)
        supabase.table("quiz_questions").delete().eq("video_id", video_id).execute()

        # Insert new questions
        questions_to_insert = []
        for q in quiz_data.questions:
            # Map frontend model to DB model
            # Frontend: options is list of strings, correctAnswer is index
            # DB: options is array, correct_answer is the string value
            
            correct_option_value = q.options[q.correctAnswer] if 0 <= q.correctAnswer < len(q.options) else q.options[0]
            
            questions_to_insert.append({
                "video_id": video_id,
                "question_text": q.question,
                "question_type": "multiple_choice", # Defaulting to MCQ for now
                "options": q.options,
                "correct_answer": correct_option_value,
                "difficulty": "medium", # Default
                "points": q.points,
                "created_at": datetime.utcnow().isoformat()
            })

        if questions_to_insert:
            response = supabase.table("quiz_questions").insert(questions_to_insert).execute()
            if not response.data:
                raise HTTPException(status_code=500, detail="Failed to save questions")

        return {"message": "Quiz created successfully", "count": len(questions_to_insert)}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create quiz error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/teacher/list")
async def list_teacher_quizzes(
    current_user: dict = Depends(get_current_teacher)
):
    """
    List quizzes (videos with questions) for the teacher
    """
    try:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            return []

        teacher_id = current_user["id"]

        # Get videos by teacher
        videos_response = supabase.table("videos").select("id, title").eq("uploaded_by", teacher_id).execute()
        if not videos_response.data:
            return []
        
        video_ids = [v["id"] for v in videos_response.data]
        video_map = {v["id"]: v["title"] for v in videos_response.data}

        # Get question counts per video
        # Supabase doesn't support easy GROUP BY count in one go via JS client syntax easily without rpc
        # So we'll fetch unique video_ids from quiz_questions that match our list
        
        questions_response = supabase.table("quiz_questions")\
            .select("video_id")\
            .in_("video_id", video_ids)\
            .execute()
            
        # Count questions per video
        quiz_counts = {}
        for q in questions_response.data:
            vid = q["video_id"]
            quiz_counts[vid] = quiz_counts.get(vid, 0) + 1
            
        # Format response
        quizzes = []
        for vid, count in quiz_counts.items():
            quizzes.append({
                "id": vid, # Using video_id as quiz_id
                "title": video_map.get(vid, "Unknown"),
                "question_count": count,
                "created_at": datetime.utcnow().isoformat() # Mock date as we don't have quiz table
            })
            
        return quizzes

    except Exception as e:
        logger.error(f"List teacher quizzes error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/video/{video_id}/questions", response_model=List[QuizQuestionResponse])
async def get_video_questions(
    video_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get quiz questions for a video
    Auto-generate questions from transcript if not exist (ML service)
    """
    try:
        # Check if Supabase is configured
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            logger.warning("Supabase not configured, returning mock questions")
            return [
                {
                    "id": str(uuid.uuid4()),
                    "video_id": video_id,
                    "question_text": "What is the main topic covered in this video?",
                    "question_type": "multiple_choice",
                    "options": ["Python Basics", "Web Development", "Data Science", "Machine Learning"],
                    "difficulty": "easy",
                    "timestamp": 30.0
                },
                {
                    "id": str(uuid.uuid4()),
                    "video_id": video_id,
                    "question_text": "Which programming language is discussed?",
                    "question_type": "multiple_choice",
                    "options": ["Java", "Python", "C++", "JavaScript"],
                    "difficulty": "easy",
                    "timestamp": 120.0
                },
                {
                    "id": str(uuid.uuid4()),
                    "video_id": video_id,
                    "question_text": "The instructor recommends starting with variables and data types.",
                    "question_type": "true_false",
                    "options": ["True", "False"],
                    "difficulty": "medium",
                    "timestamp": 240.0
                }
            ]
        
        # Get questions from database
        response = supabase.table("quiz_questions")\
            .select("id, video_id, question_text, question_type, options, difficulty, timestamp")\
            .eq("video_id", video_id)\
            .execute()
        
        if not response.data or len(response.data) == 0:
            # TODO: Trigger ML service to auto-generate questions
            # from app.workers.tasks import generate_quiz_questions
            # generate_quiz_questions.delay(video_id)
            
            logger.info(f"No questions found for video {video_id}. ML service should generate them.")
            return []
        
        return response.data
    
    except Exception as e:
        logger.error(f"Get questions error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/video/{video_id}/generate", response_model=dict)
async def generate_questions(
    video_id: str,
    num_questions: Optional[int] = 5,
    difficulty: Optional[QuestionDifficulty] = QuestionDifficulty.MEDIUM,
    current_user: dict = Depends(get_current_admin)
):
    """
    Manually trigger question generation for a video
    ML service will analyze transcript and generate questions
    """
    try:
        # Verify video exists
        if settings.SUPABASE_URL and settings.SUPABASE_KEY:
            video_response = supabase.table("videos").select("*").eq("id", video_id).execute()
            
            if not video_response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Video not found"
                )
        
        # TODO: Trigger ML service
        # from app.workers.tasks import generate_quiz_questions
        # task = generate_quiz_questions.delay(video_id, num_questions, difficulty)
        
        return {
            "message": "Question generation started",
            "video_id": video_id,
            "num_questions": num_questions,
            "difficulty": difficulty,
            "status": "processing"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generate questions error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/questions", response_model=QuizQuestionResponse)
async def create_question(
    question: QuizQuestionCreate,
    current_user: dict = Depends(get_current_admin)
):
    """
    Manually create a quiz question (Admin only)
    """
    try:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            return {
                "id": str(uuid.uuid4()),
                "video_id": question.video_id,
                "question_text": question.question_text,
                "question_type": question.question_type,
                "options": question.options,
                "difficulty": question.difficulty,
                "timestamp": question.timestamp
            }
        
        question_data = {
            "video_id": question.video_id,
            "question_text": question.question_text,
            "question_type": question.question_type,
            "options": question.options,
            "correct_answer": question.correct_answer,
            "difficulty": question.difficulty,
            "timestamp": question.timestamp,
            "explanation": question.explanation,
            "created_at": datetime.utcnow().isoformat()
        }
        
        response = supabase.table("quiz_questions").insert(question_data).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create question"
            )
        
        created = response.data[0]
        
        return {
            "id": created["id"],
            "video_id": created["video_id"],
            "question_text": created["question_text"],
            "question_type": created["question_type"],
            "options": created["options"],
            "difficulty": created["difficulty"],
            "timestamp": created.get("timestamp")
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create question error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/start/{video_id}", response_model=QuizSession)
async def start_quiz_session(
    video_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Start a quiz session for a video
    Creates a new session and returns questions
    """
    try:
        # Check if Supabase is configured
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            logger.warning("Supabase not configured, returning mock session")
            session_id = str(uuid.uuid4())
            mock_questions = [
                {
                    "id": str(uuid.uuid4()),
                    "video_id": video_id,
                    "question_text": "What is the main topic?",
                    "question_type": "multiple_choice",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": "Option A",
                    "difficulty": "medium",
                    "timestamp": None,
                    "explanation": None
                }
            ]
            
            return {
                "id": session_id,
                "user_id": current_user.get("id", "mock-user"),
                "video_id": video_id,
                "questions": mock_questions,
                "started_at": datetime.utcnow(),
                "completed_at": None,
                "score": None
            }
        
        # Get questions for this video
        questions_response = supabase.table("quiz_questions")\
            .select("*")\
            .eq("video_id", video_id)\
            .execute()
        
        if not questions_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No quiz questions available for this video"
            )
        
        # Create quiz session
        session_data = {
            "user_id": current_user["id"],
            "video_id": video_id,
            "started_at": datetime.utcnow().isoformat(),
            "total_questions": len(questions_response.data)
        }
        
        session_response = supabase.table("quiz_sessions").insert(session_data).execute()
        
        if not session_response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create quiz session"
            )
        
        session = session_response.data[0]
        
        return {
            "id": session["id"],
            "user_id": session["user_id"],
            "video_id": session["video_id"],
            "questions": questions_response.data,
            "started_at": session["started_at"],
            "completed_at": None,
            "score": None
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Start quiz error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/answer", response_model=AnswerResult)
async def submit_answer(
    session_id: str,
    answer: UserAnswer,
    current_user: dict = Depends(get_current_user)
):
    """
    Submit an answer to a question
    Validates answer and records result
    """
    try:
        # Check if Supabase is configured
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            logger.warning("Supabase not configured, returning mock result")
            return {
                "question_id": answer.question_id,
                "is_correct": True,
                "correct_answer": answer.user_answer,
                "explanation": "This is a mock explanation"
            }
        
        # Get the question
        question_response = supabase.table("quiz_questions")\
            .select("*")\
            .eq("id", answer.question_id)\
            .execute()
        
        if not question_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        question = question_response.data[0]
        is_correct = question["correct_answer"].strip().lower() == answer.user_answer.strip().lower()
        
        # Record user answer
        answer_data = {
            "session_id": session_id,
            "question_id": answer.question_id,
            "user_answer": answer.user_answer,
            "is_correct": is_correct,
            "answered_at": datetime.utcnow().isoformat()
        }
        
        supabase.table("user_answers").insert(answer_data).execute()
        
        return {
            "question_id": answer.question_id,
            "is_correct": is_correct,
            "correct_answer": question["correct_answer"],
            "explanation": question.get("explanation")
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Submit answer error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/complete/{session_id}", response_model=QuizResult)
async def complete_quiz(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Complete quiz and get results
    Calculates final score and updates session
    """
    try:
        # Check if Supabase is configured
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            logger.warning("Supabase not configured, returning mock results")
            return {
                "session_id": session_id,
                "total_questions": 5,
                "correct_answers": 4,
                "score_percentage": 80.0,
                "time_taken": 300,
                "answers": []
            }
        
        # Get session
        session_response = supabase.table("quiz_sessions")\
            .select("*")\
            .eq("id", session_id)\
            .execute()
        
        if not session_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz session not found"
            )
        
        session = session_response.data[0]
        
        # Get all answers for this session
        answers_response = supabase.table("user_answers")\
            .select("*")\
            .eq("session_id", session_id)\
            .execute()
        
        answers = answers_response.data if answers_response.data else []
        total_questions = session["total_questions"]
        correct_answers = sum(1 for ans in answers if ans["is_correct"])
        score_percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        # Calculate time taken
        started_at = datetime.fromisoformat(session["started_at"].replace('Z', '+00:00'))
        completed_at = datetime.utcnow()
        time_taken = int((completed_at - started_at).total_seconds())
        
        # Update session
        supabase.table("quiz_sessions")\
            .update({
                "completed_at": completed_at.isoformat(),
                "score": int(score_percentage),
                "correct_answers": correct_answers
            })\
            .eq("id", session_id)\
            .execute()
        
        # Get detailed answer results
        answer_results = []
        for ans in answers:
            question = supabase.table("quiz_questions")\
                .select("correct_answer, explanation")\
                .eq("id", ans["question_id"])\
                .execute()
            
            if question.data:
                answer_results.append({
                    "question_id": ans["question_id"],
                    "is_correct": ans["is_correct"],
                    "correct_answer": question.data[0]["correct_answer"],
                    "explanation": question.data[0].get("explanation")
                })
        
        return {
            "session_id": session_id,
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "score_percentage": score_percentage,
            "time_taken": time_taken,
            "answers": answer_results
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Complete quiz error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/leaderboard/{video_id}")
async def get_leaderboard(
    video_id: str,
    limit: int = 10
):
    """
    Get top scorers for a video (gamification)
    """
    try:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            return {
                "video_id": video_id,
                "leaderboard": [
                    {"rank": 1, "name": "Student A", "score": 95, "time_taken": 180},
                    {"rank": 2, "name": "Student B", "score": 90, "time_taken": 200},
                    {"rank": 3, "name": "Student C", "score": 85, "time_taken": 220}
                ]
            }
        
        # Get top sessions for this video
        sessions_response = supabase.table("quiz_sessions")\
            .select("*, users(full_name)")\
            .eq("video_id", video_id)\
            .not_.is_("completed_at", "null")\
            .order("score", desc=True)\
            .order("completed_at", desc=False)\
            .limit(limit)\
            .execute()
        
        if not sessions_response.data:
            return {"video_id": video_id, "leaderboard": []}
        
        leaderboard = []
        for idx, session in enumerate(sessions_response.data, 1):
            started = datetime.fromisoformat(session["started_at"].replace('Z', '+00:00'))
            completed = datetime.fromisoformat(session["completed_at"].replace('Z', '+00:00'))
            time_taken = int((completed - started).total_seconds())
            
            leaderboard.append({
                "rank": idx,
                "user_name": session.get("users", {}).get("full_name", "Anonymous"),
                "score": session["score"],
                "time_taken": time_taken,
                "completed_at": session["completed_at"]
            })
        
        return {
            "video_id": video_id,
            "leaderboard": leaderboard
        }
    
    except Exception as e:
        logger.error(f"Leaderboard error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
