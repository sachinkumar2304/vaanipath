import os
import json
import logging
import redis
from functools import wraps
from typing import Optional, Any, Union
from app.config import settings
import pickle

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.memory_cache: Dict[str, Any] = {}
        self.use_redis = False
        
        # Try to connect to Redis
        try:
            if settings.REDIS_URL:
                self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=False)
                self.redis_client.ping()
                self.use_redis = True
                logger.info("✅ Connected to Redis cache")
            else:
                logger.warning("⚠️ REDIS_URL not set, using in-memory cache")
        except Exception as e:
            logger.warning(f"⚠️ Failed to connect to Redis: {e}. Using in-memory cache")
            self.use_redis = False

    def get(self, key: str) -> Optional[Any]:
        try:
            if self.use_redis and self.redis_client:
                data = self.redis_client.get(key)
                if data:
                    return pickle.loads(data)
            else:
                return self.memory_cache.get(key)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
        return None

    def set(self, key: str, value: Any, ttl: int = 300):
        try:
            if self.use_redis and self.redis_client:
                pickled_data = pickle.dumps(value)
                self.redis_client.setex(key, ttl, pickled_data)
            else:
                self.memory_cache[key] = value
                # Note: In-memory cache doesn't implement TTL cleanup in this simple version
        except Exception as e:
            logger.error(f"Cache set error: {e}")

    def delete(self, key: str):
        try:
            if self.use_redis and self.redis_client:
                self.redis_client.delete(key)
            else:
                if key in self.memory_cache:
                    del self.memory_cache[key]
        except Exception as e:
            logger.error(f"Cache delete error: {e}")

    def delete_pattern(self, pattern: str):
        """Delete all keys matching pattern"""
        try:
            if self.use_redis and self.redis_client:
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
            else:
                # Simple prefix matching for in-memory
                keys_to_delete = [k for k in self.memory_cache.keys() if k.startswith(pattern.replace('*', ''))]
                for k in keys_to_delete:
                    del self.memory_cache[k]
        except Exception as e:
            logger.error(f"Cache delete pattern error: {e}")

# Global cache instance
cache = CacheService()

def cached(ttl: int = 300, key_prefix: str = ""):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key based on function name and arguments
            # Filter out 'current_user' or other dynamic args if needed, 
            # but for now we include everything to be safe
            
            # Create a simple string representation of args for the key
            # Note: This is a basic implementation. For complex objects, might need better serialization
            arg_str = str(args) + str(sorted(kwargs.items()))
            cache_key = f"{key_prefix}:{func.__name__}:{hash(arg_str)}"
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.info(f"⚡ Cache hit for {cache_key}")
                return cached_value
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            cache.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator
