"""Repositories for collections and collection items."""

from typing import Any, cast
from uuid import UUID

from sqlalchemy import CursorResult, delete, select
from sqlalchemy.orm import Session, selectinload

from app.db.repository import Repository
from app.models.collection import Collection, CollectionItem


class CollectionRepository(Repository[Collection]):
    """Persistence for Collection."""

    def __init__(self, session: Session) -> None:
        super().__init__( session,Collection)  

    def list_for_user(self, user_id: UUID) -> list[Collection]:
        stmt = (
            select(Collection)
            .where(Collection.user_id == user_id)
            .order_by(Collection.created_at.desc())
        )
        return list(self._session.scalars(stmt))

    def get_for_user(self, collection_id: UUID, user_id: UUID) -> Collection | None:
        stmt = (
            select(Collection)
            .where(Collection.id == collection_id, Collection.user_id == user_id)
            .options(selectinload(Collection.items).selectinload(CollectionItem.analysis))
        )
        return self._session.scalar(stmt)


class CollectionItemRepository(Repository[CollectionItem]):
    """Persistence for CollectionItem."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, CollectionItem)  # model class comes first

    def exists(self, collection_id: UUID, analysis_id: UUID) -> bool:
        stmt = select(CollectionItem.id).where(
            CollectionItem.collection_id == collection_id,
            CollectionItem.analysis_id == analysis_id,
        )
        return self._session.scalar(stmt) is not None

    def remove(self, collection_id: UUID, analysis_id: UUID) -> int:
        stmt = delete(CollectionItem).where(
            CollectionItem.collection_id == collection_id,
            CollectionItem.analysis_id == analysis_id,
        )
        result = cast(CursorResult[Any], self._session.execute(stmt))
        return result.rowcount or 0
