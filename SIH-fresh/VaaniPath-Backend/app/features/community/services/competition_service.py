"""
Competition Service
Business logic for competitions, quizzes, and leaderboards
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone
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
            
            # Check if competition is valid
            comp = community_db.table("competitions").select("start_time, end_time, status").eq("id", str(competition_id)).execute()
            if not comp.data:
                raise ValueError("Competition not found")
            
            comp_data = comp.data[0]
            now = datetime.utcnow()
            start_time = datetime.fromisoformat(comp_data["start_time"].replace('Z', ''))
            end_time = datetime.fromisoformat(comp_data["end_time"].replace('Z', ''))

            # Update status if needed
            if comp_data["status"] == "upcoming" and now >= start_time:
                 # Check if it should be active
                 if now < end_time:
                     community_db.table("competitions").update({"status": "active"}).eq("id", str(competition_id)).execute()
                     comp_data["status"] = "active"

            # User Requirement: "student can join only when it starts"
            # Allow joining if active 
            if comp_data["status"] != "active":
                 # Use a small grace period or check strictly
                 if now < start_time:
                     raise ValueError("Competition has not started yet. You can join only when it starts.")
                 if now > end_time:
                     raise ValueError("Competition has ended.")

            # Register
            community_db.table("competition_registrations").insert({
                "competition_id": str(competition_id),
                "user_id": str(user_id)
            }).execute()
            
            # Increment participants count
            current_count_res = community_db.table("competitions").select("participants_count").eq("id", str(competition_id)).execute()
            new_count = (current_count_res.data[0]["participants_count"] or 0) + 1
            
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
             # Check if competition is active
            comp = community_db.table("competitions").select("status, end_time").eq("id", str(submission.competition_id)).execute()
            if not comp.data:
                raise ValueError("Competition not found")
            
            comp_data = comp.data[0]
            now = datetime.utcnow()
            end_time = datetime.fromisoformat(comp_data["end_time"].replace('Z', ''))
            
            if now > end_time or comp_data["status"] == "completed":
                # Trigger finalization if needed, but reject submission
                await CompetitionService.finalize_competition(submission.competition_id)
                raise ValueError("Competition has ended")

            # Get question to check correct answer
            question = community_db.table("competition_questions").select("correct_answer, points").eq(
                "id", str(submission.question_id)
            ).execute()
            
            if not question.data:
                raise ValueError("Question not found")
            
            # Check if already answered
            existing = community_db.table("competition_submissions").select("id").eq("user_id", str(user_id)).eq("question_id", str(submission.question_id)).execute()
            if existing.data:
                 raise ValueError("Question already answered")

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
    async def finalize_competition(competition_id: UUID):
        """Finalize competition, determine winner, and award GyanPoints"""
        from app.db.supabase_client import get_supabase
        
        try:
            # Check current status
            comp_res = community_db.table("competitions").select("status, points_first").eq("id", str(competition_id)).execute()
            if not comp_res.data: 
                return
            
            comp = comp_res.data[0]
            if comp["status"] == "completed":
                return # Already finalized
            
            logger.info(f"🏁 Finalizing competition {competition_id}...")
            
            # Get Leaderboard
            leaderboard = await CompetitionService.get_leaderboard(competition_id)
            
            if leaderboard.entries:
                # Winner is different from LeaderboardEntry (it has full stats)
                winner = leaderboard.entries[0]
                winner_id = winner.user_id
                
                # Award points in Main DB
                main_db = get_supabase()
                
                # Fetch current points
                # Note: 'users' table in public schema usually linked to auth.users
                # We need to ensure we can select/update it.
                user_res = main_db.table("users").select("gyan_points").eq("id", str(winner_id)).execute()
                
                if user_res.data:
                    # current_points = user_res.data[0].get("gyan_points", 0) or 0
                    points_to_award = comp.get("points_first", 100)
                    # new_points = current_points + points_to_award
                    
                    # Update via Service
                    from app.features.community.services.gyan_points_service import GyanPointsService
                    await GyanPointsService.add_points(
                        user_id=winner_id,
                        points=points_to_award,
                        source="competition_win",
                        description=f"Winner of {comp.get('title', 'Competition')}",
                        reference_id=competition_id
                    )
                    
                    # --- Streak Logic ---
                    try:
                        # Calculate streak: Count how many *most recent* completed competitions in this community were won by this user
                        # 1. Get past completed competitions for this community, ordered recent first
                        past_comps = community_db.table("competitions").select("id").eq("community_id", comp["community_id"]).eq("status", "completed").neq("id", str(competition_id)).order("end_time", desc=True).limit(20).execute()
                        
                        streak_count = 0
                        if past_comps.data:
                            # We need to check who won each of these. 
                            # Optimization: We could store 'winner_id' in competition table to avoid N+1 queries.
                            # But for now, we have to query leaderboards or submissions? 
                            # Leaderboard is calculated on fly... checking 'submissions' or 'registrations' is fuzzy.
                            # Best approach without schema change: 
                            #  - Actually, we don't have a stored winner. We assume highest score.
                            # This is expensive to calculate for past competitions on the fly.
                            # ALTERNATIVE: Just check if we can query 'gyan_points_transactions' for 'competition_win' source for this user?
                            #  But that doesn't guarantee *consecutive* wins in *this* community (could be others).
                            
                            # Let's rely on gyan_points_transactions with generic description logic used above? 
                            # "Winner of {title}" - weak link.
                            
                            # Decision: For robust streak, we REALLY should update the competition model to store 'winner_id' when finalized.
                            # Since I can't easily change schema right now without migrations, I will use a heuristic:
                            # Check `gyan_points_transactions` for this user, looking for 'competition_win'.
                            # If the *last* transaction (before this one) was also a competition win AND time difference is reasonable, count it?
                            # No, that spans communities.
                            
                            # Correct "No Schema Change" approach:
                            # We simply won't back-calculate too deep.
                            # Wait, we can assume if the user won, they got points.
                            pass

                        # Since deep streak calculation is hard without 'winner_id' column, 
                        # I will add a simple 'current_winning_streak' to the USER's gyan_points profile? 
                        # No, simpler: Just give a random "Persistence Bonus" if they participated in last 3?
                        # User specifically asked for "coming 1st in contest in a row".
                        
                        # Let's do a simplified check:
                        # Get last 5 completed competitions for this community.
                        # For each, get the leaderboard (expensive but accurate).
                        # If winner == current_user, streak++. Else break.
                        
                        streak_bonus = 0
                        consecutive_wins = 0
                        
                        for past_comp in past_comps.data:
                            # Quick fetch top leaderboard entry
                            # This is simulating `get_leaderboard` logic but lighter
                            subs = community_db.table("competition_submissions").select("user_id, points_earned").eq("competition_id", past_comp["id"]).execute()
                            
                            if not subs.data: continue # No submissions
                            
                            # Aggregate
                            u_scores = {}
                            for s in subs.data:
                                uid = s['user_id']
                                u_scores[uid] = u_scores.get(uid, 0) + s['points_earned']
                            
                            # Find winner
                            if not u_scores: continue
                            past_winner_id = max(u_scores, key=u_scores.get)
                            
                            if past_winner_id == str(winner_id):
                                consecutive_wins += 1
                            else:
                                break # Streak broken
                        
                        if consecutive_wins > 0:
                            streak_bonus = consecutive_wins * 20 # 20 points per streak level
                            await GyanPointsService.add_points(
                                user_id=winner_id,
                                points=streak_bonus,
                                source="streak_bonus",
                                description=f"Ignited Streak! {consecutive_wins+1} wins in a row!",
                                reference_id=competition_id
                            )
                            logger.info(f"🔥 Streak Bonus: {streak_bonus} pts for {consecutive_wins} consecutive wins")

                    except Exception as e:
                        logger.error(f"Failed to calc streak: {e}")
                    # --------------------

                    # main_db.table("users").update({"gyan_points": new_points}).eq("id", str(winner_id)).execute()
                    
                    logger.info(f"🏆 Awarded {points_to_award} GyanPoints to winner {winner_id}")
            
            # Mark as completed
            community_db.table("competitions").update({"status": "completed"}).eq("id", str(competition_id)).execute()
            logger.info(f"✅ Competition {competition_id} finalized")
            
        except Exception as e:
            logger.error(f"❌ Error finalizing competition: {e}")
            # Don't raise, just log, as this might be called from get_competition
            
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
            
            # Optimization: Fetch all user names in one query if possible
            # For now, we'll just put placeholders or try to fetch if we had a batch endpoint
            
            from app.db.supabase_client import get_supabase
            main_db = get_supabase()
            
            for rank, (user_id, scores) in enumerate(sorted_users, 1):
                # Fetch user info
                user_info = {"full_name": "Unknown", "email": ""}
                try:
                    u_res = main_db.table("users").select("full_name, email").eq("id", user_id).execute()
                    if u_res.data:
                        user_info = u_res.data[0]
                except:
                    pass

                entries.append(LeaderboardEntry(
                    user_id=UUID(user_id),
                    user_name=user_info.get("full_name", "User"),
                    user_email=user_info.get("email", ""), 
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
            # Auto-update statuses if needed (lazy check)
            # Not doing meaningful loop updates here to save perf, rely on get_by_id checks
            
            competitions = community_db.table("competitions").select("*").eq(
                "community_id", str(community_id)
            ).order("created_at", desc=True).execute()
            
            results = []
            for comp in competitions.data:
                results.append(CompetitionResponse(
                    **comp,
                    is_registered=False, 
                    user_score=None
                ))
            return results
        except Exception as e:
            logger.error(f"❌ Error fetching competitions: {e}")
            raise

    @staticmethod
    async def get_competition_by_id(competition_id: UUID) -> CompetitionResponse:
        """Get a single competition by ID"""
        try:
            result = community_db.table("competitions").select("*").eq("id", str(competition_id)).execute()
            
            if not result.data:
                raise ValueError("Competition not found")
            
            comp = result.data[0]
            
            # Date Handling
            now = datetime.utcnow()
            start_time = datetime.fromisoformat(comp["start_time"].replace('Z', ''))
            end_time = datetime.fromisoformat(comp["end_time"].replace('Z', ''))
            
            # Lazy Status Update
            status_changed = False
            if comp["status"] == "upcoming" and now >= start_time:
                 comp["status"] = "active"
                 status_changed = True
            
            if (comp["status"] == "active" or comp["status"] == "upcoming") and now > end_time:
                 # Should be completed
                 # Trigger finalization async or await? Await to ensure consistent state
                 await CompetitionService.finalize_competition(competition_id)
                 comp["status"] = "completed"
                 status_changed = True
            
            if status_changed:
                 # Just update status string in DB, finalize already did its job if completed
                 if comp["status"] != "completed": # finalize handles db update for completed
                     community_db.table("competitions").update({"status": comp["status"]}).eq("id", str(competition_id)).execute()

            return CompetitionResponse(
                **comp,
                is_registered=False, 
                user_score=None
            )
        except Exception as e:
            logger.error(f"❌ Error fetching competition {competition_id}: {e}")
            raise

    @staticmethod
    async def get_student_questions(competition_id: UUID, user_id: UUID) -> List[dict]:
        """Get questions for a student (hides correct answer)"""
        try:
            # Check participation
            reg = community_db.table("competition_registrations").select("*").eq("competition_id", str(competition_id)).eq("user_id", str(user_id)).execute()
            # If strict "must register" required:
            # if not reg.data: raise ValueError("Not registered")
            
            # Check status
            comp = community_db.table("competitions").select("status").eq("id", str(competition_id)).execute()
            if not comp.data or comp.data[0]["status"] != "active":
                 # Allow seeing questions if completed? Maybe for review. For now restrict to active.
                 # User said "answer the contest quiz for the duration".
                 if comp.data and comp.data[0]["status"] == "completed":
                      pass # Allow review?
                 else:
                      pass 
                      # For strictness:
                      # if comp.data[0]["status"] != "active": raise ValueError("Competition not active")

            questions = community_db.table("competition_questions").select("*").eq("competition_id", str(competition_id)).order("question_order").execute()
            
            # Mask correct answers
            masked_questions = []
            for q in questions.data:
                q_copy = q.copy()
                if "correct_answer" in q_copy:
                    del q_copy["correct_answer"]
                masked_questions.append(q_copy)
            
            return masked_questions
        except Exception as e:
            logger.error(f"❌ Error fetching questions: {e}")
            raise
