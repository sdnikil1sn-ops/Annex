"""Redis client tests using fakeredis."""

import fakeredis
from redis import Redis

from app.infra.redis_client import get_redis


def test_get_redis_returns_client() -> None:
    """get_redis must return a configured Redis client without connecting."""
    client = get_redis()
    assert isinstance(client, Redis)


def test_redis_commands_with_fakeredis() -> None:
    """Redis command semantics verified against fakeredis (test mock)."""
    client = fakeredis.FakeRedis(decode_responses=True)
    assert client.set("annex:smoke", "ok") is True
    assert client.get("annex:smoke") == "ok"
