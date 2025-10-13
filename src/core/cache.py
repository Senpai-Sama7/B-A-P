"""
Async Redis cache connection and management.
"""
import redis.asyncio as aioredis
from typing import Optional, Any
import json
from src.config import get_settings

settings = get_settings()

class CacheManager:
    """Redis cache manager for handling connections and operations."""
    
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
        self.url = settings.REDIS_URL
    
    async def connect(self) -> "CacheManager":
        """Connect to Redis and return the cache manager instance."""
        if not self.redis:
            try:
                self.redis = await aioredis.from_url(
                    self.url,
                    encoding="utf-8",
                    decode_responses=True,
                    max_connections=20,
                )
            except Exception as e:
                # Log the error or handle it appropriately
                raise ConnectionError(f"Failed to connect to Redis: {e}") from e
        return self
    
    async def close(self):
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()
            self.redis = None
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        if not self.redis:
            await self.connect()
        value = await self.redis.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in cache with optional TTL."""
        if not self.redis:
            await self.connect()
        if not isinstance(value, str):
            value = json.dumps(value)
        if ttl:
            return await self.redis.setex(key, ttl, value)
        return await self.redis.set(key, value)
    
    async def delete(self, key: str) -> int:
        """Delete a key from cache."""
        if not self.redis:
            await self.connect()
        return await self.redis.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        if not self.redis:
            await self.connect()
        return await self.redis.exists(key) > 0
    
    async def clear(self) -> bool:
        """Clear all keys from cache."""
        if not self.redis:
            await self.connect()
        return await self.redis.flushdb()

# Global cache manager instance
cache_manager = CacheManager()

async def get_redis() -> CacheManager:
    """Dependency for getting Redis cache in FastAPI."""
    if not cache_manager.redis:
        await cache_manager.connect()
    return cache_manager
