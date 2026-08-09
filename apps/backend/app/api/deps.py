"""Shared API dependencies."""

from fastapi import Depends
from sqlalchemy.orm import Session
from supabase import create_client

from app.core.config import get_settings
from app.db.session import get_db
from app.infra.storage import MediaStorage, SupabaseMediaStorage
from app.repositories.alert import AlertRepository
from app.repositories.analysis import AnalysisRepository
from app.repositories.collection import CollectionItemRepository, CollectionRepository
from app.repositories.notification import NotificationRepository
from app.services.alert import AlertService
from app.services.analysis import AnalysisService
from app.services.collection import CollectionService
from app.services.notification import NotificationService


def get_analysis_service(db: Session = Depends(get_db)) -> AnalysisService:
    """Build an AnalysisService bound to the request session."""
    return AnalysisService(AnalysisRepository(db))

def get_collection_service(db: Session = Depends(get_db)) -> CollectionService:
    return CollectionService(
        CollectionRepository(db),
        CollectionItemRepository(db),
        AnalysisRepository(db),
    )


def get_alert_service(db: Session = Depends(get_db)) -> AlertService:
    return AlertService(AlertRepository(db))


def get_notification_service(db: Session = Depends(get_db)) -> NotificationService:
    return NotificationService(NotificationRepository(db))

def get_media_storage() -> MediaStorage:
    """Provide the Supabase-backed media storage dependency."""
    settings = get_settings()
    client = create_client(settings.supabase_url, settings.supabase_service_role_key)
    return SupabaseMediaStorage(client, settings.storage_bucket)