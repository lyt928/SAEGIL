from __future__ import annotations

import base64
from functools import lru_cache
from io import BytesIO

from fastapi import APIRouter, HTTPException, Query
from PIL import Image

from apps.backend.config.settings import get_settings
from apps.backend.schemas.events import EventClearResponse, EventListResponse, EventResponse, HealthResponse
from apps.backend.schemas.inference import (
    ImageInferRequest,
    ImageInferResponse,
    InferRequest,
    InferResponse,
)
from apps.backend.schemas.zones import ZoneDeleteResponse, ZoneListResponse, ZonePayload, ZoneResponse
from apps.backend.services.pipeline import process_frame
from apps.backend.services.zone_store import JsonZoneStore
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


def get_zone_store() -> JsonZoneStore:
    settings = get_settings()
    return JsonZoneStore(path=settings.zone_path)


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
def get_recent_events(
    limit: int = Query(default=20, ge=1, le=200),
    event_type: str | None = Query(default=None),
    severity: str | None = Query(default=None),
) -> EventListResponse:
    settings = get_settings()
    logger = JsonlEventLogger(path=settings.log_path)
    events = logger.read_recent_events(limit=limit)

    if event_type is not None:
        normalized_type = event_type.strip().lower()
        events = [event for event in events if str(event.get("type", "")).lower() == normalized_type]

    if severity is not None:
        normalized_severity = severity.strip().lower()
        events = [event for event in events if str(event.get("severity", "")).lower() == normalized_severity]

    return EventListResponse(events=events)


@router.get("/events/{event_id}", response_model=EventResponse)
def get_event(event_id: str) -> EventResponse:
    settings = get_settings()
    logger = JsonlEventLogger(path=settings.log_path)
    event = logger.read_event(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return EventResponse(event=event)


@router.delete("/events", response_model=EventClearResponse)
def clear_events() -> EventClearResponse:
    settings = get_settings()
    logger = JsonlEventLogger(path=settings.log_path)
    logger.clear()
    return EventClearResponse(cleared=True)


@router.get("/zones", response_model=ZoneListResponse)
def list_zones() -> ZoneListResponse:
    store = get_zone_store()
    return ZoneListResponse(zones=[ZonePayload(**zone) for zone in store.read_all()])


@router.get("/zones/{zone_id}", response_model=ZoneResponse)
def get_zone(zone_id: str) -> ZoneResponse:
    store = get_zone_store()
    zone = store.read_one(zone_id)
    if zone is None:
        raise HTTPException(status_code=404, detail="Zone not found")
    return ZoneResponse(zone=ZonePayload(**zone))


@router.post("/zones", response_model=ZoneResponse)
def create_or_update_zone(zone: ZonePayload) -> ZoneResponse:
    store = get_zone_store()
    saved = store.upsert(zone.model_dump(exclude_none=True))
    return ZoneResponse(zone=ZonePayload(**saved))


@router.delete("/zones/{zone_id}", response_model=ZoneDeleteResponse)
def delete_zone(zone_id: str) -> ZoneDeleteResponse:
    store = get_zone_store()
    deleted = store.delete(zone_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Zone not found")
    return ZoneDeleteResponse(deleted=True)
