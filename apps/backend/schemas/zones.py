from __future__ import annotations

from pydantic import BaseModel, Field


class ZonePayload(BaseModel):
    # 구역은 최소 3개 이상의 점으로 이루어진 다각형으로 정의합니다.
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
