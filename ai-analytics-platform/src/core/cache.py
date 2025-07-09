import os
import redis
from typing import Any

REDIS_URL = os.environ["REDIS_URL"]  # Fail fast if missing

redis_client = redis.Redis.from_url(REDIS_URL)

def get_redis() -> Any:
    """Return a Redis client instance."""
    return redis_client
