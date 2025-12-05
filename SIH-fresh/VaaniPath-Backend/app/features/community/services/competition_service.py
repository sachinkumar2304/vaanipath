"""
Competition Service
Business logic for competitions, quizzes, and leaderboards
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from app.features.community.database import community_db
from app.features.community.models.competition import (
    CompetitionCreate, CompetitionUpdate, CompetitionResponse, CompetitionList,
    QuestionCreate, QuestionResponse, SubmissionCreate, SubmissionResponse,
    Leaderboard, LeaderboardEntry
)
import logging

logger = logging.getLogger(__name__)


class CompetitionService:
    """Service for managing competitions"""
    
    @staticmethod
    async def create_competition(comp_data: CompetitionCreate, user_id: UUID) -> CompetitionResponse:
        """Create a new competition"""
        try:
            result = community_db.table("competitions").insert({
                "community_id": str(comp_data.community_id),
                "created_by": str(user_id),
                "title": comp_data.title,
                "description": comp_data.description,
                "start_time": comp_data.start_time.isoformat(),
                "end_time": comp_data.end_time.isoformat(),
                "max_participants": comp_data.max_participants,
                "points_first": comp_data.points_first,
                "points_second": comp_data.points_second,
                "points_third": comp_data.points_third,
                "points_top10": comp_data.points_top10
            }).execute()
            
            competition = result.data[0]
            
            logger.info(f"✅ Competition created: {comp_data.title} by user {user_id}")
            
            return CompetitionResponse(**competition, is_registered=False, user_score=None)
            
        except Exception as e:
            logger.error(f"❌ Error creating competition: {e}")
            raise
    
    @staticmethod
    async def add_questions(competition_id: UUID, questions: List[QuestionCreate], user_id: UUID) -> List[QuestionResponse]:
        """Add questions to a competition"""
        try:
            # Verify user is the creator
            comp = community_db.table("competitions").select("created_by").eq("id", str(competition_id)).execute()
            if not comp.data or comp.data[0]["created_by"] != str(user_id):
                raise ValueError("Only the creator can add questions")
            
            # Insert questions
            questions_data = []
            for q in questions:
                questions_data.append({
                    "competition_id": str(competition_id),
                    "question_text": q.question_text,
                    "options": [opt.dict() for opt in q.options],
                    "correct_answer": q.correct_answer,
                    "points": q.points,
                    "question_order": q.question_order
                })
            
            result = community_db.table("competition_questions").insert(questions_data).execute()
            
            # Update total_questions count
            community_db.table("competitions").update({
                "total_questions": len(questions_data)
            }).eq("id", str(competition_id)).execute()
            
            logger.info(f"✅ Added {len(questions_data)} questions to competition {competition_id}")
            
            return [QuestionResponse(**q) for q in result.data]
            
        except Exception as e:
            logger.error(f"❌ Error adding questions: {e}")
            raise
    
    @staticmethod
    async def register_for_competition(competition_id: UUID, user_id: UUID) -> dict:
        """Register a user for a competition"""
        try:
            # Check if already registered
            existing = community_db.table("competition_registrations").select("*").eq(
                "competition_id", str(competition_id)
            ).eq("user_id", str(user_id)).execute()
            
            if existing.data:
                return {"message": "Already registered"}
            
            # Check if competition has started
            comp = community_db.table("competitions").select("start_time, status").eq("id", str(competition_id)).execute()
            if comp.data[0]["status"] != "upcoming":
                raise ValueError("Cannot register for a competition that has already started")
            
            # Register
            community_db.table("competition_registrations").insert({
                "competition_id": str(competition_id),
                "user_id": str(user_id)
            }).execute()
            
            # Increment participants count
            comp_data = community_db.table("competitions").select("participants_count").eq("id", str(competition_id)).execute()
            new_count = comp_data.data[0]["participants_count"] + 1
            
            community_db.table("competitions").update({
                "participants_count": new_count
            }).eq("id", str(competition_id)).execute()
            
            logger.info(f"✅ User {user_id} registered for competition {competition_id}")
            
            return {"message": "Successfully registered"}
            
        except Exception as e:
            logger.error(f"❌ Error registering for competition: {e}")
            raise
    
    @staticmethod
    async def submit_answer(submission: SubmissionCreate, user_id: UUID) -> SubmissionResponse:
        """Submit an answer to a competition question"""
        try:
            # Get question to check correct answer
            question = community_db.table("competition_questions").select("correct_answer, points").eq(
                "id", str(submission.question_id)
            ).execute()
            
            if not question.data:
                raise ValueError("Question not found")
            
            is_correct = question.data[0]["correct_answer"] == submission.selected_answer
            points_earned = question.data[0]["points"] if is_correct else 0
            
            # Insert submission
            result = community_db.table("competition_submissions").insert({
                "competition_id": str(submission.competition_id),
                "user_id": str(user_id),
                "question_id": str(submission.question_id),
                "selected_answer": submission.selected_answer,
                "is_correct": is_correct,
                "points_earned": points_earned
            }).execute()
            
            return SubmissionResponse(**result.data[0])
            
        except Exception as e:
            logger.error(f"❌ Error submitting answer: {e}")
            raise
    
    @staticmethod
    async def get_leaderboard(competition_id: UUID) -> Leaderboard:
        """Get competition leaderboard"""
        try:
            # Get all submissions for this competition
            submissions = community_db.table("competition_submissions").select(
                "user_id, points_earned, is_correct"
            ).eq("competition_id", str(competition_id)).execute()
            
            # Aggregate scores by user
            user_scores = {}
            for sub in submissions.data:
                user_id = sub["user_id"]
                if user_id not in user_scores:
                    user_scores[user_id] = {
                        "total_score": 0,
                        "correct_answers": 0,
                        "total_answers": 0
                    }
                
                user_scores[user_id]["total_score"] += sub["points_earned"]
                user_scores[user_id]["total_answers"] += 1
                if sub["is_correct"]:
                    user_scores[user_id]["correct_answers"] += 1
            
            # Sort by score
            sorted_users = sorted(
                user_scores.items(),
                key=lambda x: (x[1]["total_score"], x[1]["correct_answers"]),
                reverse=True
            )
            
            # Create leaderboard entries
            entries = []
            for rank, (user_id, scores) in enumerate(sorted_users, 1):
                # TODO: Fetch user info from main DB
                entries.append(LeaderboardEntry(
                    user_id=UUID(user_id),
                    user_name="User",  # Placeholder
                    user_email="user@example.com",  # Placeholder
                    total_score=scores["total_score"],
                    correct_answers=scores["correct_answers"],
                    total_answers=scores["total_answers"],
                    rank=rank
                ))
            
            return Leaderboard(
                entries=entries,
                total_participants=len(entries)
            )
            
        except Exception as e:
            logger.error(f"❌ Error fetching leaderboard: {e}")
            raise
    @staticmethod
    async def get_competitions_by_community(community_id: UUID) -> List[CompetitionResponse]:
        """Get all competitions for a specific community"""
        try:
            competitions = community_db.table("competitions").select("*").eq(
                "community_id", str(community_id)
            ).order("created_at", desc=True).execute()
            
            # Map simple dictionary to Pydantic model
            # Note: client might need to handle is_registered checks separately or loop here
            # For simplicity, returning list.
            results = []
            for comp in competitions.data:
                results.append(CompetitionResponse(
                    **comp,
                    is_registered=False, # TODO: Check registration status for current user if needed
                    user_score=None
                ))
            return results
        except Exception as e:
            logger.error(f"❌ Error fetching competitions: {e}")
            raise
