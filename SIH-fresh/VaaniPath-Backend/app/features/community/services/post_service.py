"""
Post Service
Business logic for community posts, likes, replies, and threading
"""
from typing import List, Optional
from uuid import UUID
from app.features.community.database import community_db
from app.features.community.models.post import (
    PostCreate, PostUpdate, PostResponse, PostList,
    ReplyCreate, ReplyResponse, ReplyList
)
import logging

logger = logging.getLogger(__name__)


class PostService:
    """Service for managing posts and interactions"""
    
    @staticmethod
    async def create_post(post_data: PostCreate, user_id: UUID, user_info: dict) -> PostResponse:
        """Create a new post"""
        try:
            # Insert post
            result = community_db.table("community_posts").insert({
                "community_id": str(post_data.community_id),
                "user_id": str(user_id),
                "content": post_data.content,
                "media_urls": post_data.media_urls or [],
                "post_type": post_data.post_type,
                "course_id": str(post_data.course_id) if post_data.course_id else None,
                "is_pinned": post_data.post_type == "announcement"  # Auto-pin announcements
            }).execute()
            
            post = result.data[0]
            
            # Increment post count
            community = community_db.table("communities").select("post_count").eq(
                "id", str(post_data.community_id)
            ).execute()
            new_count = community.data[0]["post_count"] + 1
            
            community_db.table("communities").update({
                "post_count": new_count
            }).eq("id", str(post_data.community_id)).execute()
            
            logger.info(f"✅ Post created in community {post_data.community_id} by user {user_id}")
            
            return PostResponse(
                **post,
                user_name=user_info.get("full_name"),
                user_email=user_info.get("email"),
                is_liked_by_user=False
            )
            
        except Exception as e:
            logger.error(f"❌ Error creating post: {e}")
            raise
    
    @staticmethod
    async def get_posts(
        community_id: UUID,
        page: int = 1,
        page_size: int = 20,
        user_id: Optional[UUID] = None
    ) -> PostList:
        """Get posts for a community"""
        try:
            offset = (page - 1) * page_size
            
            # Get posts (pinned first, then by created_at)
            result = community_db.table("community_posts").select("*").eq(
                "community_id", str(community_id)
            ).order("is_pinned", desc=True).order("created_at", desc=True).range(
                offset, offset + page_size - 1
            ).execute()
            
            # Get total count
            count_result = community_db.table("community_posts").select("id", count="exact").eq(
                "community_id", str(community_id)
            ).execute()
            total = count_result.count if hasattr(count_result, 'count') else len(count_result.data)
            
            posts = []
            for post in result.data:
                # Check if user liked this post
                is_liked = False
                if user_id:
                    like_result = community_db.table("post_likes").select("id").eq(
                        "post_id", post["id"]
                    ).eq("user_id", str(user_id)).execute()
                    is_liked = len(like_result.data) > 0
                
                # TODO: Fetch user info from main DB
                posts.append(PostResponse(
                    **post,
                    user_name="User",  # Placeholder
                    user_email="user@example.com",  # Placeholder
                    is_liked_by_user=is_liked
                ))
            
            return PostList(
                posts=posts,
                total=total,
                page=page,
                page_size=page_size
            )
            
        except Exception as e:
            logger.error(f"❌ Error fetching posts: {e}")
            raise
    
    @staticmethod
    async def toggle_like(post_id: UUID, user_id: UUID) -> dict:
        """Like or unlike a post"""
        try:
            # Check if already liked
            existing = community_db.table("post_likes").select("*").eq(
                "post_id", str(post_id)
            ).eq("user_id", str(user_id)).execute()
            
            if existing.data:
                # Unlike
                community_db.table("post_likes").delete().eq(
                    "post_id", str(post_id)
                ).eq("user_id", str(user_id)).execute()
                
                # Decrement likes count
                post = community_db.table("community_posts").select("likes_count").eq("id", str(post_id)).execute()
                new_count = max(0, post.data[0]["likes_count"] - 1)
                
                community_db.table("community_posts").update({
                    "likes_count": new_count
                }).eq("id", str(post_id)).execute()
                
                return {"message": "Post unliked", "liked": False, "likes_count": new_count}
            else:
                # Like
                community_db.table("post_likes").insert({
                    "post_id": str(post_id),
                    "user_id": str(user_id)
                }).execute()
                
                # Increment likes count
                post = community_db.table("community_posts").select("likes_count").eq("id", str(post_id)).execute()
                new_count = post.data[0]["likes_count"] + 1
                
                community_db.table("community_posts").update({
                    "likes_count": new_count
                }).eq("id", str(post_id)).execute()
                
                return {"message": "Post liked", "liked": True, "likes_count": new_count}
                
        except Exception as e:
            logger.error(f"❌ Error toggling like: {e}")
            raise
    
    @staticmethod
    async def create_reply(reply_data: ReplyCreate, user_id: UUID, user_info: dict) -> ReplyResponse:
        """Create a reply to a post"""
        try:
            # Insert reply
            result = community_db.table("post_replies").insert({
                "post_id": str(reply_data.post_id),
                "user_id": str(user_id),
                "parent_reply_id": str(reply_data.parent_reply_id) if reply_data.parent_reply_id else None,
                "content": reply_data.content
            }).execute()
            
            reply = result.data[0]
            
            # Increment replies count on post
            post = community_db.table("community_posts").select("replies_count").eq(
                "id", str(reply_data.post_id)
            ).execute()
            new_count = post.data[0]["replies_count"] + 1
            
            community_db.table("community_posts").update({
                "replies_count": new_count
            }).eq("id", str(reply_data.post_id)).execute()
            
            logger.info(f"✅ Reply created on post {reply_data.post_id} by user {user_id}")
            
            return ReplyResponse(
                **reply,
                user_name=user_info.get("full_name"),
                user_email=user_info.get("email"),
                is_liked_by_user=False
            )
            
        except Exception as e:
            logger.error(f"❌ Error creating reply: {e}")
            raise
    
    @staticmethod
    async def get_replies(post_id: UUID, user_id: Optional[UUID] = None) -> ReplyList:
        """Get replies for a post (with threading support)"""
        try:
            # Get all replies for this post
            result = community_db.table("post_replies").select("*").eq(
                "post_id", str(post_id)
            ).order("created_at", desc=False).execute()
            
            replies = []
            for reply in result.data:
                # Check if user liked this reply
                is_liked = False
                if user_id:
                    like_result = community_db.table("reply_likes").select("id").eq(
                        "reply_id", reply["id"]
                    ).eq("user_id", str(user_id)).execute()
                    is_liked = len(like_result.data) > 0
                
                # TODO: Fetch user info from main DB
                replies.append(ReplyResponse(
                    **reply,
                    user_name="User",  # Placeholder
                    user_email="user@example.com",  # Placeholder
                    is_liked_by_user=is_liked
                ))
            
            return ReplyList(
                replies=replies,
                total=len(replies)
            )
            
        except Exception as e:
            logger.error(f"❌ Error fetching replies: {e}")
            raise
