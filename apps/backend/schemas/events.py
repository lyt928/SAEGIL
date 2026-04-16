from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str


class EventListResponse(BaseModel):
    events: list[dict[str, Any]] = Field(default_factory=list)


class EventResponse(BaseModel):
    event: dict[str, Any]


class EventClearResponse(BaseModel):
    cleared: bool
