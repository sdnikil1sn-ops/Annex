"""Database round-trip tests (require TEST_DATABASE_URL + applied migrations)."""

from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.analysis import Analysis, AnalysisStatus, AnalysisType
from app.models.collection import Collection, CollectionItem
from app.models.user import User


def test_user_roundtrip(db_session: Session) -> None:
    """A user must persist and be retrievable by id."""
    user = User(
        email=f"user-{uuid4().hex}@example.com",
        display_name="Phase Three",
    )
    db_session.add(user)
    db_session.commit()

    fetched = db_session.get(User, user.id)
    assert fetched is not None
    assert fetched.display_name == "Phase Three"


def test_analysis_roundtrip(db_session: Session) -> None:
    """An analysis must persist its type, status, and input payload."""
    user = User(email=f"analysis-{uuid4().hex}@example.com")
    db_session.add(user)
    db_session.commit()

    analysis = Analysis(
        user_id=user.id,
        type=AnalysisType.URL,
        status=AnalysisStatus.PENDING,
        title="Example Article",
        input_payload={"url": "https://example.com/article"},
    )
    db_session.add(analysis)
    db_session.commit()

    fetched = db_session.get(Analysis, analysis.id)
    assert fetched is not None
    assert fetched.type == AnalysisType.URL
    assert fetched.input_payload["url"] == "https://example.com/article"


def test_collection_hierarchy(db_session: Session) -> None:
    """Collection items must link a collection to an analysis."""
    user = User(email=f"collection-{uuid4().hex}@example.com")
    db_session.add(user)
    db_session.commit()

    analysis = Analysis(
        user_id=user.id,
        type=AnalysisType.TEXT,
        status=AnalysisStatus.COMPLETED,
    )
    collection = Collection(user_id=user.id, name="Research")
    db_session.add_all([analysis, collection])
    db_session.commit()

    item = CollectionItem(collection_id=collection.id, analysis_id=analysis.id)
    db_session.add(item)
    db_session.commit()

    assert db_session.get(CollectionItem, item.id) is not None
