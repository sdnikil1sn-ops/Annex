"""Sliding-window rate limiting primitives.

An in-memory implementation is provided now; a Redis-backed implementation
replaces it in the caching phase without changing the RateLimiter protocol.
"""

import time
from collections import deque
from dataclasses import dataclass
from typing import Protocol

from cachetools import TTLCache


@dataclass(frozen=True)
class RateLimitDecision:
    """Result of a rate-limit check."""

    allowed: bool
    retry_after_seconds: int = 0


class RateLimiter(Protocol):
    """Interface every rate limiter (in-memory, Redis) must implement."""

    def check(self, key: str, now: float | None = None) -> RateLimitDecision:
        """Return whether a request for ``key`` is allowed within the window."""
        ...


class InMemorySlidingWindowRateLimiter:
    """Sliding-window limiter keeping hit timestamps in memory.

    Expired keys are evicted automatically by a TTLCache, so the table cannot
    grow without bound under high traffic.
    """

    def __init__(
        self,
        max_requests: int,
        window_seconds: int,
        max_keys: int = 10_000,
    ) -> None:
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._hits: TTLCache[str, deque[float]] = TTLCache(
            maxsize=max_keys,
            ttl=window_seconds,
        )

    def check(self, key: str, now: float | None = None) -> RateLimitDecision:
        """Check and record a request for ``key`` against the sliding window."""
        current = now if now is not None else time.monotonic()
        default_queue: deque[float] = deque()
        hits = self._hits.setdefault(key, default_queue)

        # Drop timestamps that have fallen outside the window.
        while hits and current - hits[0] >= self._window_seconds:
            hits.popleft()

        if len(hits) >= self._max_requests:
            retry_after = max(1, int(self._window_seconds - (current - hits[0])))
            return RateLimitDecision(allowed=False, retry_after_seconds=retry_after)

        hits.append(current)
        return RateLimitDecision(allowed=True)
