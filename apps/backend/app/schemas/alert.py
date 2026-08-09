"""Alert request/response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.alert import AlertFrequency


class AlertCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    query: dict[str, object] = Field(default_factory=dict)
    frequency: AlertFrequency = AlertFrequency.DAILY


class AlertUpdate(BaseModel):
    name: str | None = None
    query: dict[str, object] | None = None
    frequency: AlertFrequency | None = None
    is_active: bool | None = None


class AlertRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    query: dict[str, object]
    frequency: str
    is_active: bool
    last_triggered_at: datetime | None = None
    created_at: datetime
