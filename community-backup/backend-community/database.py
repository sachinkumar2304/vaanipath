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
        
        # Use community-specific credentials if available, otherwise fall back to main
        supabase_url = settings.COMMUNITY_SUPABASE_URL or settings.SUPABASE_URL
        supabase_key = settings.COMMUNITY_SUPABASE_KEY or settings.SUPABASE_KEY
        
        if not supabase_url or not supabase_key:
            raise ValueError("Supabase credentials not configured for community features")
        
        _community_supabase = create_client(supabase_url, supabase_key)
        
        if settings.COMMUNITY_SUPABASE_URL:
            logger.info("✅ Community Supabase client initialized (dedicated)")
        else:
            logger.info("✅ Community Supabase client initialized (using main credentials)")
    
    return _community_supabase


# Convenience alias
community_db = get_community_db()
