from __future__ import annotations

import base64
from functools import lru_cache
from io import BytesIO

from fastapi import APIRouter, HTTPException, Query
from PIL import Image

from apps.backend.config.settings import get_settings
from apps.backend.schemas.events import EventListResponse, HealthResponse
from apps.backend.schemas.inference import (
    ImageInferRequest,
    ImageInferResponse,
    InferRequest,
    InferResponse,
)
from apps.backend.services.pipeline import process_frame
from core.detection.mock_detector import get_mock_detections
from core.detection.yolo_detector import YoloDetector
from core.logging.event_logger import JsonlEventLogger


router = APIRouter()


@lru_cache
def get_detector() -> YoloDetector:
    settings = get_settings()
    return YoloDetector(
        model_path=settings.model_path,
        allowed_labels={"person", "helmet", "vest"},
    )


def _decode_image_base64(image_base64: str) -> Image.Image:
    raw_value = image_base64.strip()
    if "," in raw_value and raw_value.lower().startswith("data:image"):
        raw_value = raw_value.split(",", 1)[1]

    try:
        image_bytes = base64.b64decode(raw_value, validate=True)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail="Invalid image_base64 payload") from exc

    try:
        image = Image.open(BytesIO(image_bytes))
        return image.convert("RGB")
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail="Decoded payload is not a valid image") from exc


def _get_image_detections(request: ImageInferRequest) -> list[dict]:
    detector_mode = request.detector_mode.strip().lower()

    if detector_mode == "mock":
        return get_mock_detections(request.mock_scenario)

    if detector_mode != "real":
        raise HTTPException(status_code=400, detail="detector_mode must be either 'real' or 'mock'")

    if not request.image_base64:
        raise HTTPException(status_code=400, detail="image_base64 is required when detector_mode is 'real'")

    detector = get_detector()
    image = _decode_image_base64(request.image_base64)
    return detector.predict_as_dicts(image)


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok")


@router.post("/infer", response_model=InferResponse)
def run_inference(request: InferRequest) -> InferResponse:
    settings = get_settings()
    logger = JsonlEventLogger(path=settings.log_path)

    result = process_frame(
        detections=[item.model_dump() for item in request.detections],
        zones=[item.model_dump(exclude_none=True) for item in request.zones],
        logger=logger,
    )
    return InferResponse(**result)


@router.post("/infer/image", response_model=ImageInferResponse)
def run_image_inference(request: ImageInferRequest) -> ImageInferResponse:
    settings = get_settings()
    logger = JsonlEventLogger(path=settings.log_path)
    detections = _get_image_detections(request)
    result = process_frame(
        detections=detections,
        zones=[item.model_dump(exclude_none=True) for item in request.zones],
        logger=logger,
    )
    return ImageInferResponse(detections=detections, **result)


@router.get("/events", response_model=EventListResponse)
def get_recent_events(limit: int = Query(default=20, ge=1, le=200)) -> EventListResponse:
    settings = get_settings()
    logger = JsonlEventLogger(path=settings.log_path)
    return EventListResponse(events=logger.read_recent_events(limit=limit))
