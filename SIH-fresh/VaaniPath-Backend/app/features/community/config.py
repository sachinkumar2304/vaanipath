"""
Community Feature Configuration
Loads separate Supabase credentials for community database
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class CommunitySettings(BaseSettings):
    """Community-specific settings"""
    COMMUNITY_SUPABASE_URL: str
    COMMUNITY_SUPABASE_KEY: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_community_settings() -> CommunitySettings:
    return CommunitySettings()
