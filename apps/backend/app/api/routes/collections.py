"""Collection endpoints (authenticated, ownership-scoped)."""

from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from app.api.deps import get_collection_service
from app.models.user import User
from app.schemas.collection import (
    CollectionCreate,
    CollectionItemAdd,
    CollectionRead,
)
from app.services.auth import get_current_user
from app.services.collection import CollectionService

router = APIRouter(prefix="/collections", tags=["collections"])


@router.post("", response_model=CollectionRead, status_code=status.HTTP_201_CREATED)
def create_collection(
    payload: CollectionCreate,
    current_user: User = Depends(get_current_user),
    service: CollectionService = Depends(get_collection_service),
) -> CollectionRead:
    return service.create(current_user.id, payload.name, payload.description)  # type: ignore[return-value]


@router.get("", response_model=list[CollectionRead])
def list_collections(
    current_user: User = Depends(get_current_user),
    service: CollectionService = Depends(get_collection_service),
) -> list[CollectionRead]:
    return service.list_for_user(current_user.id)  # type: ignore[return-value]


@router.get("/{collection_id}", response_model=CollectionRead)
def get_collection(
    collection_id: UUID,
    current_user: User = Depends(get_current_user),
    service: CollectionService = Depends(get_collection_service),
) -> CollectionRead:
    return service.get_for_user(collection_id, current_user.id)  # type: ignore[return-value]


@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_collection(
    collection_id: UUID,
    current_user: User = Depends(get_current_user),
    service: CollectionService = Depends(get_collection_service),
) -> Response:
    service.delete_for_user(collection_id, current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{collection_id}/analyses", status_code=status.HTTP_200_OK)
def add_analysis_to_collection(
    collection_id: UUID,
    payload: CollectionItemAdd,
    current_user: User = Depends(get_current_user),
    service: CollectionService = Depends(get_collection_service),
) -> dict[str, str]:
    """Add an analysis to a collection (idempotent)."""
    service.add_analysis(collection_id, payload.analysis_id, current_user.id)
    return {"status": "added"}


@router.delete("/{collection_id}/analyses/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_analysis_from_collection(
    collection_id: UUID,
    analysis_id: UUID,
    current_user: User = Depends(get_current_user),
    service: CollectionService = Depends(get_collection_service),
) -> Response:
    service.remove_analysis(collection_id, analysis_id, current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
