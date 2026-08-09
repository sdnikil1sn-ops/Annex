"""API v1 router aggregator.

Every feature router added in later phases is included here so the main
application only ever mounts one versioned router.
"""
from fastapi import APIRouter

from app.api.routes import alerts, analyses, collections, health, media, notifications, users
from app.core.config import get_settings

settings = get_settings()

api_router = APIRouter(prefix=settings.api_prefix)
api_router.include_router(health.router)
api_router.include_router(users.router)
api_router.include_router(analyses.router)  
api_router.include_router(collections.router)
api_router.include_router(alerts.router)
api_router.include_router(notifications.router)
api_router.include_router(media.router)
