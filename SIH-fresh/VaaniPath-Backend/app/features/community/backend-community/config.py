"""
Community Feature Configuration
Loads separate Supabase credentials for community database
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class CommunitySettings(BaseSettings):
    """Community-specific settings"""
    COMMUNITY_SUPABASE_URL: Optional[str] = None
    COMMUNITY_SUPABASE_KEY: Optional[str] = None
    
    # Fallback to main Supabase if community-specific not set
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_community_settings() -> CommunitySettings:
    return CommunitySettings()
