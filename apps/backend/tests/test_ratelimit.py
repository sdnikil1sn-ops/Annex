"""Unit tests for the in-memory sliding-window rate limiter."""

from app.core.ratelimit import InMemorySlidingWindowRateLimiter


def test_allows_within_limit() -> None:
    """Requests under the limit must be allowed."""
    limiter = InMemorySlidingWindowRateLimiter(max_requests=3, window_seconds=10)
    for _ in range(3):
        assert limiter.check("user:1").allowed is True


def test_blocks_over_limit() -> None:
    """Requests over the limit must be rejected with a retry window."""
    limiter = InMemorySlidingWindowRateLimiter(max_requests=2, window_seconds=10)
    limiter.check("user:1", now=100.0)
    limiter.check("user:1", now=101.0)
    decision = limiter.check("user:1", now=102.0)
    assert decision.allowed is False
    assert decision.retry_after_seconds > 0


def test_window_expires() -> None:
    """Once the window passes, requests are allowed again."""
    limiter = InMemorySlidingWindowRateLimiter(max_requests=1, window_seconds=10)
    limiter.check("user:1", now=100.0)
    assert limiter.check("user:1", now=105.0).allowed is False
    assert limiter.check("user:1", now=110.0).allowed is True


def test_keys_are_isolated() -> None:
    """Different keys must not share the same allowance."""
    limiter = InMemorySlidingWindowRateLimiter(max_requests=1, window_seconds=10)
    assert limiter.check("user:a", now=100.0).allowed is True
    assert limiter.check("user:b", now=100.0).allowed is True
