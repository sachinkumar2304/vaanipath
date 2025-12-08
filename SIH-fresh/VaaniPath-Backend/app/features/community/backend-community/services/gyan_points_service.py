from uuid import UUID
from typing import Optional, List
from app.features.community.database import community_db
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class GyanPointsService:
    @staticmethod
    async def get_user_points(user_id: UUID) -> int:
        """Get total points for a user"""
        try:
            result = community_db.table("gyan_points").select("total_points").eq("user_id", str(user_id)).execute()
            if result.data:
                return result.data[0]["total_points"]
            
            # Initialize if not exists
            community_db.table("gyan_points").insert({"user_id": str(user_id), "total_points": 0}).execute()
            return 0
        except Exception as e:
            logger.error(f"Error fetching user points: {e}")
            return 0

    @staticmethod
    async def get_history(user_id: UUID) -> List[dict]:
        """Get point transaction history"""
        try:
            result = community_db.table("gyan_points_transactions").select("*").eq(
                "user_id", str(user_id)
            ).order("created_at", desc=True).limit(50).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error fetching points history: {e}")
            return []

    @staticmethod
    async def add_points(user_id: UUID, points: int, source: str, description: str, reference_id: Optional[UUID] = None) -> int:
        """Add points to user account"""
        try:
            # 1. Get current points
            current = await GyanPointsService.get_user_points(user_id)
            new_total = current + points
            
            # 2. Update/Insert entries
            # Using upsert requires knowing the ID, so update directly since get_user_points ensures existence
            community_db.table("gyan_points").update({
                "total_points": new_total,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("user_id", str(user_id)).execute()
            
            # 3. Log transaction
            community_db.table("gyan_points_transactions").insert({
                "user_id": str(user_id),
                "points_change": points,
                "transaction_type": source,
                "description": description,
                "reference_id": str(reference_id) if reference_id else None
            }).execute()
            
            return new_total
        except Exception as e:
            logger.error(f"Error adding points: {e}")
            raise
