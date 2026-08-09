"""Health-check endpoints used by CI, load balancers, and orchestrators."""

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings

router = APIRouter(tags=["health"])


def health_payload(settings: Settings) -> dict[str, str]:
    """Return the canonical health payload for a settings instance."""
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.version,
        "environment": settings.environment,
    }


@router.get("/health", summary="Health check (versioned)")
def health(settings: Settings = Depends(get_settings)) -> dict[str, str]:
    """Return service status under the versioned API prefix."""
    return health_payload(settings)
