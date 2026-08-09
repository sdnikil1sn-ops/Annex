"""Collection service (ownership-scoped)."""

from uuid import UUID

from app.core.errors import NotFoundError
from app.models.collection import Collection, CollectionItem
from app.repositories.analysis import AnalysisRepository
from app.repositories.collection import CollectionItemRepository, CollectionRepository


class CollectionService:
    """Ownership-scoped operations on collections and their items."""

    def __init__(
        self,
        collections: CollectionRepository,
        items: CollectionItemRepository,
        analyses: AnalysisRepository,
    ) -> None:
        self._collections = collections
        self._items = items
        self._analyses = analyses

    def create(self, user_id: UUID, name: str, description: str | None) -> Collection:
        collection = Collection(
            user_id=user_id,
            name=name,
            description=description,
        )
        return self._collections.add(collection)

    def list_for_user(self, user_id: UUID) -> list[Collection]:
        return self._collections.list_for_user(user_id)

    def get_for_user(self, collection_id: UUID, user_id: UUID) -> Collection:
        collection = self._collections.get_for_user(collection_id, user_id)
        if collection is None:
            raise NotFoundError("Collection not found")
        return collection

    def delete_for_user(self, collection_id: UUID, user_id: UUID) -> None:
        collection = self.get_for_user(collection_id, user_id)
        self._collections.delete(collection)

    def add_analysis(self, collection_id: UUID, analysis_id: UUID, user_id: UUID) -> None:
        # Ownership checks.
        self.get_for_user(collection_id, user_id)
        analysis = self._analyses.get(analysis_id)
        if analysis is None or analysis.user_id != user_id:
            raise NotFoundError("Analysis not found")

        # Idempotent: skip if the analysis is already in the collection.
        if self._items.exists(collection_id, analysis_id):
            return

        item = CollectionItem(collection_id=collection_id, analysis_id=analysis_id)
        self._items.add(item)

    def remove_analysis(self, collection_id: UUID, analysis_id: UUID, user_id: UUID) -> None:
        self.get_for_user(collection_id, user_id)
        removed = self._items.remove(collection_id, analysis_id)
        if removed == 0:
            raise NotFoundError("Analysis not in collection")
