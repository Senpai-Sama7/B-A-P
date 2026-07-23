"""
Async Redis cache connection and management.
"""

import json
from typing import Any, Optional, cast

import redis.asyncio as aioredis

from src.config import get_settings

settings = get_settings()


class CacheManager:
    """Redis cache manager for handling connections and operations."""

    def __init__(self) -> None:
        self.redis: Optional[aioredis.Redis] = None
        self.url = settings.REDIS_URL

    async def connect(self) -> "CacheManager":
        """Connect to Redis and return the cache manager instance."""
        if not self.redis:
            try:
                self.redis = cast(
                    aioredis.Redis,
                    await aioredis.from_url(  # type: ignore[no-untyped-call]
                        self.url,
                        encoding="utf-8",
                        decode_responses=True,
                        max_connections=20,
                    ),
                )
            except Exception as e:
                raise ConnectionError(f"Failed to connect to Redis: {e}") from e
        return self

    async def close(self) -> None:
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()
            self.redis = None

    async def _client(self) -> aioredis.Redis:
        """Return an active Redis client, connecting if needed."""
        if not self.redis:
            await self.connect()
        assert self.redis is not None
        return self.redis

    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        redis = await self._client()
        value = await redis.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in cache with optional TTL."""
        redis = await self._client()
        stored_value = value if isinstance(value, str) else json.dumps(value)
        if ttl:
            return bool(await redis.setex(key, ttl, stored_value))
        return bool(await redis.set(key, stored_value))

    async def delete(self, key: str) -> int:
        """Delete a key from cache."""
        redis = await self._client()
        return int(await redis.delete(key))

    async def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        redis = await self._client()
        return bool(await redis.exists(key) > 0)

    async def clear(self) -> bool:
        """Clear all keys from cache."""
        redis = await self._client()
        return bool(await redis.flushdb())


# Global cache manager instance
cache_manager = CacheManager()


async def get_redis() -> CacheManager:
    """Dependency for getting Redis cache in FastAPI."""
    if not cache_manager.redis:
        await cache_manager.connect()
    return cache_manager
