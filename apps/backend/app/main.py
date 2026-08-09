"""FastAPI application entrypoint for the ANNEX backend."""

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.api.routes import health
from app.core.config import Settings, get_settings
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging
from app.core.middleware import (
    RateLimitMiddleware,
    RequestIDMiddleware,
    SecurityHeadersMiddleware,
)
from app.core.ratelimit import InMemorySlidingWindowRateLimiter

settings = get_settings()
configure_logging(settings)

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="REST API for the ANNEX media & information literacy platform.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.api_prefix}/openapi.json",
)

# Middleware order matters: Starlette builds the stack with the LAST added
# middleware as the OUTERMOST. CORS is added first (innermost); the request
# ID middleware is added last so its ID covers every other layer and its
# header appears on all responses, including 429s.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    RateLimitMiddleware,
    limiter=InMemorySlidingWindowRateLimiter(
        max_requests=settings.rate_limit_requests,
        window_seconds=settings.rate_limit_window_seconds,
    ),
    enabled=settings.rate_limit_enabled,
)
app.add_middleware(
    SecurityHeadersMiddleware,
    enabled=settings.security_headers_enabled,
)
app.add_middleware(RequestIDMiddleware)

register_exception_handlers(app)

app.include_router(api_router)


@app.get("/healthz", include_in_schema=False, tags=["health"])
def healthz(settings: Settings = Depends(get_settings)) -> dict[str, str]:
    """Liveness probe for load balancers and orchestrators (unversioned)."""
    return health.health_payload(settings)


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    """Return a pointer to the interactive API documentation."""
    return {"service": settings.app_name, "docs": "/docs"}
