"""Generic SQLAlchemy repository base."""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import Base


class Repository[ModelType: Base]:
    """Generic CRUD operations for a SQLAlchemy model."""

    def __init__(self, session: Session, model: type[ModelType]) -> None:
        self._session = session
        self._model = model

    def get(self, id: object) -> ModelType | None:
        return self._session.get(self._model, id)

    def list(self) -> Sequence[ModelType]:
        return self._session.scalars(select(self._model)).all()

    def add(self, instance: ModelType) -> ModelType:
        self._session.add(instance)
        return instance

    def delete(self, instance: ModelType) -> None:
        self._session.delete(instance)
    def flush(self) -> None:
        """Flush pending changes so generated ids are populated."""
        self._session.flush()
    def commit(self) -> None:
        """Commit the current transaction."""
        self._session.commit()

