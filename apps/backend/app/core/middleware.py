"""Pure-ASGI middleware for the ANNEX backend.

Pure-ASGI (rather than BaseHTTPMiddleware) is used so that large request
bodies (image/video uploads in later phases) stream without buffering.
"""

import contextvars
import json
import uuid

from starlette.datastructures import Headers
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.ratelimit import RateLimitDecision, RateLimiter

request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id",
    default="",
)


class RequestIDMiddleware:
    """Assign a request ID to every HTTP request and echo it in the response."""

    def __init__(self, app: ASGIApp, header_name: str = "X-Request-ID") -> None:
        self.app = app
        self._header_name = header_name.encode("latin-1")

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Wrap the application, injecting the request ID into context and headers."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        request_id = headers.get("x-request-id") or uuid.uuid4().hex
        token = request_id_var.set(request_id)

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                message.setdefault("headers", []).append(
                    (self._header_name, request_id.encode("latin-1"))
                )
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            request_id_var.reset(token)


class SecurityHeadersMiddleware:
    """Apply security hardening headers to every HTTP response."""

    _DEFAULT_HEADERS: tuple[tuple[bytes, bytes], ...] = (
        (b"X-Content-Type-Options", b"nosniff"),
        (b"X-Frame-Options", b"DENY"),
        (b"Referrer-Policy", b"strict-origin-when-cross-origin"),
        (b"Permissions-Policy", b"camera=(), microphone=(), geolocation=()"),
        (
            b"Content-Security-Policy",
            (
                b"default-src 'self'; "
                b"script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                b"style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                b"img-src 'self' data:; "
                b"font-src 'self' data:; "
                b"connect-src 'self'"
            ),
        ),
    )

    def __init__(self, app: ASGIApp, *, enabled: bool = True) -> None:
        self.app = app
        self._enabled = enabled

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Wrap the application, adding security headers to HTTP responses."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        if not self._enabled:
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                message.setdefault("headers", []).extend(self._DEFAULT_HEADERS)
            await send(message)

        await self.app(scope, receive, send_wrapper)


class RateLimitMiddleware:
    """Enforce a sliding-window request limit per client IP and route."""

    def __init__(
        self,
        app: ASGIApp,
        limiter: RateLimiter,
        *,
        enabled: bool = True,
        exempt_paths: set[str] | None = None,
        exempt_prefixes: tuple[str, ...] = ("/docs", "/redoc", "openapi.json"),
    ) -> None:
        self.app = app
        self._limiter = limiter
        self._enabled = enabled
        self._exempt_paths = exempt_paths or {"/healthz"}
        self._exempt_prefixes = exempt_prefixes

    def _is_exempt(self, path: str) -> bool:
        """Return whether a path is exempt from rate limiting."""
        if path in self._exempt_paths:
            return True
        return any(path.startswith(prefix) for prefix in self._exempt_prefixes)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Wrap the application, rejecting requests that exceed the limit."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        if not self._enabled or self._is_exempt(scope["path"]):
            await self.app(scope, receive, send)
            return

        client = scope.get("client")
        client_ip = client[0] if client else "unknown"
        key = f"{client_ip}:{scope['path']}"

        decision = self._limiter.check(key)
        if not decision.allowed:
            await self._send_rate_limited(send, decision)
            return
        await self.app(scope, receive, send)

    async def _send_rate_limited(self, send: Send, decision: RateLimitDecision) -> None:
        """Emit a 429 response with a Retry-After header."""
        body = json.dumps(
            {
                "error": {
                    "code": "rate_limited",
                    "message": "Too many requests. Please try again shortly.",
                    "request_id": request_id_var.get(),
                }
            }
        ).encode("utf-8")
        headers: list[tuple[bytes, bytes]] = [
            (b"content-type", b"application/json"),
            (b"retry-after", str(decision.retry_after_seconds).encode("ascii")),
        ]
        await send({"type": "http.response.start", "status": 429, "headers": headers})
        await send({"type": "http.response.body", "body": body})
