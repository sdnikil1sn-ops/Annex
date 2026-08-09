"""ORM models. Importing this package registers every model with Base.metadata."""
from app.models.alert import Alert, AlertFrequency
from app.models.analysis import Analysis, AnalysisStatus, AnalysisType
from app.models.claim import Claim, ClaimStatus
from app.models.collection import Collection, CollectionItem
from app.models.evidence import Evidence
from app.models.notification import Notification, NotificationType
from app.models.source import Source
from app.models.user import User

__all__ = [
    "Alert",
    "AlertFrequency",
    "Analysis",
    "AnalysisStatus",
    "AnalysisType",
    "Collection",
    "CollectionItem",
    "Notification",
    "NotificationType",
    "User",
    "Claim",
    "ClaimStatus",
    "Evidence",
    "Source",
]
