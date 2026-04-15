from __future__ import annotations

from pydantic import BaseModel, Field


class ZonePayload(BaseModel):
    id: str
    points: list[list[float]] = Field(min_length=3)
    name: str | None = None
    severity: str | None = None


class ZoneListResponse(BaseModel):
    zones: list[ZonePayload] = Field(default_factory=list)


class ZoneResponse(BaseModel):
    zone: ZonePayload


class ZoneDeleteResponse(BaseModel):
    deleted: bool
