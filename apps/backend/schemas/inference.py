from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class DetectionInput(BaseModel):
    label: str
    bbox: list[int] = Field(min_length=4, max_length=4)
    track_id: int | None = None
    confidence: float | None = None


class ZoneInput(BaseModel):
    id: str
    points: list[list[float]]
    name: str | None = None
    severity: str | None = None


class InferRequest(BaseModel):
    detections: list[DetectionInput]
    zones: list[ZoneInput] = Field(default_factory=list)


class InferResponse(BaseModel):
    ppe_results: list[dict[str, Any]]
    events: list[dict[str, Any]]
    alerts: list[str]


class ImageInferRequest(BaseModel):
    image_base64: str | None = None
    detector_mode: str | None = None
    mock_scenario: str | None = None
    zones: list[ZoneInput] = Field(default_factory=list)


class ImageInferResponse(InferResponse):
    detections: list[dict[str, Any]]
