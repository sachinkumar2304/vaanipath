"""
Community Service
Business logic for community management
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from app.features.community.database import community_db
from app.features.community.models.community import (
    CommunityCreate, CommunityUpdate, CommunityResponse, CommunityList
)
import logging

logger = logging.getLogger(__name__)


class CommunityService:
    """Service for managing communities"""
    
    @staticmethod
    async def create_community(community_data: CommunityCreate, user_id: UUID) -> CommunityResponse:
        """Create a new community"""
        try:
            # Insert community
            result = community_db.table("communities").insert({
                "name": community_data.name,
                "domain": community_data.domain,
                "description": community_data.description,
                "thumbnail_url": community_data.thumbnail_url,
                "created_by": str(user_id)
            }).execute()
            
            community = result.data[0]
            
            # Auto-join creator as member with creator role
            community_db.table("community_members").insert({
                "community_id": community["id"],
                "user_id": str(user_id),
                "role": "creator"
            }).execute()
            
            # Update member count
            community_db.table("communities").update({
                "member_count": 1
            }).eq("id", community["id"]).execute()
            
            logger.info(f"✅ Community created: {community['name']} by user {user_id}")
            
            return CommunityResponse(**community, is_member=True, user_role="creator")
            
        except Exception as e:
            logger.error(f"❌ Error creating community: {e}")
            raise
    
    @staticmethod
    async def get_communities(
        page: int = 1,
        page_size: int = 20,
        domain: Optional[str] = None,
        user_id: Optional[UUID] = None
    ) -> CommunityList:
        """Get list of communities with pagination"""
        try:
            offset = (page - 1) * page_size
            
            # Build query
            query = community_db.table("communities").select("*")
            
            if domain:
                query = query.eq("domain", domain)
            
            # Get total count
            count_result = query.execute()
            total = len(count_result.data)
            
            # Get paginated results
            result = query.order("created_at", desc=True).range(offset, offset + page_size - 1).execute()
            
            communities = []
            for community in result.data:
                # Check if user is a member
                is_member = False
                user_role = None
                
                if user_id:
                    member_result = community_db.table("community_members").select("role").eq(
                        "community_id", community["id"]
                    ).eq("user_id", str(user_id)).execute()
                    
                    if member_result.data:
                        is_member = True
                        user_role = member_result.data[0]["role"]
                
                communities.append(CommunityResponse(
                    **community,
                    is_member=is_member,
                    user_role=user_role
                ))
            
            return CommunityList(
                communities=communities,
                total=total,
                page=page,
                page_size=page_size
            )
            
        except Exception as e:
            logger.error(f"❌ Error fetching communities: {e}")
            raise
    
    @staticmethod
    async def get_community(community_id: UUID, user_id: Optional[UUID] = None) -> CommunityResponse:
        """Get community by ID"""
        try:
            result = community_db.table("communities").select("*").eq("id", str(community_id)).execute()
            
            if not result.data:
                raise ValueError("Community not found")
            
            community = result.data[0]
            
            # Check if user is a member
            is_member = False
            user_role = None
            
            if user_id:
                member_result = community_db.table("community_members").select("role").eq(
                    "community_id", str(community_id)
                ).eq("user_id", str(user_id)).execute()
                
                if member_result.data:
                    is_member = True
                    user_role = member_result.data[0]["role"]
            
            return CommunityResponse(**community, is_member=is_member, user_role=user_role)
            
        except Exception as e:
            logger.error(f"❌ Error fetching community: {e}")
            raise
    
    @staticmethod
    async def join_community(community_id: UUID, user_id: UUID) -> dict:
        """Join a community"""
        try:
            # Check if already a member
            existing = community_db.table("community_members").select("*").eq(
                "community_id", str(community_id)
            ).eq("user_id", str(user_id)).execute()
            
            if existing.data:
                return {"message": "Already a member"}
            
            # Add member
            community_db.table("community_members").insert({
                "community_id": str(community_id),
                "user_id": str(user_id),
                "role": "member"
            }).execute()
            
            # Increment member count
            community = community_db.table("communities").select("member_count").eq("id", str(community_id)).execute()
            new_count = community.data[0]["member_count"] + 1
            
            community_db.table("communities").update({
                "member_count": new_count
            }).eq("id", str(community_id)).execute()
            
            logger.info(f"✅ User {user_id} joined community {community_id}")
            
            return {"message": "Successfully joined community"}
            
        except Exception as e:
            logger.error(f"❌ Error joining community: {e}")
            raise
    
    @staticmethod
    async def leave_community(community_id: UUID, user_id: UUID) -> dict:
        """Leave a community"""
        try:
            # Check if member
            member = community_db.table("community_members").select("role").eq(
                "community_id", str(community_id)
            ).eq("user_id", str(user_id)).execute()
            
            if not member.data:
                raise ValueError("Not a member of this community")
            
            # Don't allow creator to leave
            if member.data[0]["role"] == "creator":
                raise ValueError("Creator cannot leave the community")
            
            # Remove member
            community_db.table("community_members").delete().eq(
                "community_id", str(community_id)
            ).eq("user_id", str(user_id)).execute()
            
            # Decrement member count
            community = community_db.table("communities").select("member_count").eq("id", str(community_id)).execute()
            new_count = max(0, community.data[0]["member_count"] - 1)
            
            community_db.table("communities").update({
                "member_count": new_count
            }).eq("id", str(community_id)).execute()
            
            logger.info(f"✅ User {user_id} left community {community_id}")
            
            return {"message": "Successfully left community"}
            
        except Exception as e:
            logger.error(f"❌ Error leaving community: {e}")
            raise
