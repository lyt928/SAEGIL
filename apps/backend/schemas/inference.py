from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class DetectionInput(BaseModel):
    # 외부에서 직접 전달하는 detection 한 건의 형식입니다.
    label: str
    bbox: list[int] = Field(min_length=4, max_length=4)
    track_id: int | None = None
    confidence: float | None = None


class ZoneInput(BaseModel):
    # API 요청 안에서 함께 전달할 위험구역 정의 형식입니다.
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
    # 이미지 추론은 base64와 detector 모드를 함께 받습니다.
    image_base64: str | None = None
    detector_mode: str | None = None
    mock_scenario: str | None = None
    zones: list[ZoneInput] = Field(default_factory=list)


class ImageInferResponse(InferResponse):
    detections: list[dict[str, Any]]
