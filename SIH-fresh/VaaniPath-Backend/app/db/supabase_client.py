from supabase import create_client, Client
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize Supabase client
supabase: Client = None

def initialize_supabase() -> Client:
    """Initialize and return Supabase client"""
    global supabase
    
    try:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            logger.error("❌ Supabase credentials missing!")
            logger.error("   Set SUPABASE_URL and SUPABASE_KEY in .env file")
            raise ValueError("Supabase credentials not configured")
        
        # Use Service Key if available for backend operations (bypasses RLS)
        key = settings.SUPABASE_SERVICE_KEY or settings.SUPABASE_KEY
        
        supabase = create_client(
            settings.SUPABASE_URL,
            key
        )
        logger.info("Supabase client initialized successfully")
        logger.info(f"   Project: {settings.SUPABASE_URL}")
        return supabase
    except Exception as e:
        logger.error(f"❌ Failed to initialize Supabase client: {e}")
        raise

# Initialize on module load
try:
    supabase = initialize_supabase()
except Exception as e:
    logger.warning(f"Supabase initialization failed: {e}")
    supabase = None


def get_supabase() -> Client:
    """Get Supabase client instance"""
    if supabase is None:
        raise Exception(
            "Supabase client not initialized. "
            "Please check SUPABASE_URL and SUPABASE_KEY in .env file"
        )
    return supabase
