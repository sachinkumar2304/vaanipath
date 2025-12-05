import redis
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize Redis client
redis_client = None

try:
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
        decode_responses=True
    )
    # Test connection
    redis_client.ping()
    logger.info("Redis client initialized successfully")
except Exception as e:
    logger.warning(f"Redis connection failed: {e}. Task queue will not be available.")


def get_redis():
    """Get Redis client instance"""
    if redis_client is None:
        raise Exception("Redis client not initialized")
    return redis_client
