"""Redis client factory."""

from functools import lru_cache

from redis import Redis

from app.core.config import get_settings


@lru_cache
def get_redis() -> Redis:
    """Return a process-wide Redis client (created once, reused)."""
    return Redis.from_url(get_settings().redis_url, decode_responses=True)
