"""
Community Database Client
Dedicated Supabase client for community features
"""
from supabase import create_client, Client
from app.features.community.config import get_community_settings
import logging

logger = logging.getLogger(__name__)

# Global community Supabase client
_community_supabase: Client = None


def get_community_db() -> Client:
    """Get or create community Supabase client"""
    global _community_supabase
    
    if _community_supabase is None:
        settings = get_community_settings()
        _community_supabase = create_client(
            settings.COMMUNITY_SUPABASE_URL,
            settings.COMMUNITY_SUPABASE_KEY
        )
        logger.info("✅ Community Supabase client initialized")
    
    return _community_supabase


# Convenience alias
community_db = get_community_db()
