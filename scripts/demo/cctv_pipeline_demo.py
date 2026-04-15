from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np


FILE = Path(__file__).resolve()
ROOT = FILE.parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from apps.backend.config.settings import get_settings
from apps.backend.services.pipeline import process_frame
from core.detection.yolo_detector import YoloDetector
from core.logging.event_logger import JsonlEventLogger
from core.zones.polygon_zone import normalize_zone_points


def parse_args() -> argparse.Namespace:
    settings = get_settings()
    parser = argparse.ArgumentParser(description="Run the CCTV pipeline demo.")
    parser.add_argument(
        "--source",
        default=settings.camera_source,
        help="Camera index like 0 or a video file path.",
    )
    parser.add_argument(
        "--zones",
        default=str(ROOT / "data" / "samples" / "sample_zones.json"),
        help="Path to a JSON file containing zone definitions.",
    )
    parser.add_argument(
        "--model",
        default=settings.model_path,
        help="Path to the YOLO model file.",
    )
    parser.add_argument(
        "--log-path",
        default=settings.log_path,
        help="Path to the JSONL event log file.",
    )
    parser.add_argument(
        "--confidence",
        type=float,
        default=0.25,
        help="YOLO confidence threshold.",
    )
    return parser.parse_args()


def load_zones(path: str) -> list[dict]:
    with Path(path).open("r", encoding="utf-8") as file:
        return json.load(file)


def parse_source(raw_source: str) -> int | str:
    return int(raw_source) if raw_source.isdigit() else raw_source


def build_person_result_map(ppe_results: list[dict]) -> dict[tuple[int, int, int, int], dict]:
    return {tuple(item["bbox"]): item for item in ppe_results if item.get("bbox")}


def draw_zones(frame: np.ndarray, zones: list[dict], events: list[dict]) -> np.ndarray:
    overlay = frame.copy()
    active_zone_ids = {event.get("zone_id") for event in events if event.get("type") == "zone_intrusion"}

    for zone in zones:
        points = np.array(normalize_zone_points(zone), np.int32)
        if len(points) < 3:
            continue

        is_active = zone.get("id") in active_zone_ids
        color = (0, 0, 255) if is_active else (0, 200, 255)
        cv2.polylines(frame, [points], True, color, 2)
        cv2.fillPoly(overlay, [points], color)

        first_point = tuple(points[0])
        cv2.putText(
            frame,
            zone.get("name", zone.get("id", "zone")),
            (int(first_point[0]), max(int(first_point[1]) - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2,
            cv2.LINE_AA,
        )

    return cv2.addWeighted(overlay, 0.2, frame, 0.8, 0)


def draw_detections(frame: np.ndarray, detections: list[dict], ppe_results: list[dict], events: list[dict]) -> None:
    person_map = build_person_result_map(ppe_results)
    event_bboxes = {
        tuple(event["person_bbox"])
        for event in events
        if event.get("type") == "zone_intrusion" and event.get("person_bbox")
    }

    for detection in detections:
        bbox = detection.get("bbox")
        if not bbox:
            continue

        x1, y1, x2, y2 = bbox
        bbox_tuple = tuple(bbox)
        label = detection.get("label", "unknown")
        color = (255, 200, 0)

        if label == "person":
            ppe_result = person_map.get(bbox_tuple)
            has_issue = bbox_tuple in event_bboxes or (
                ppe_result is not None and (not ppe_result["has_helmet"] or not ppe_result["has_vest"])
            )
            color = (0, 0, 255) if has_issue else (0, 255, 0)

            status = []
            if ppe_result is not None:
                status.append("H:OK" if ppe_result["has_helmet"] else "H:MISS")
                status.append("V:OK" if ppe_result["has_vest"] else "V:MISS")
            label = f"person {' '.join(status)}".strip()
        elif label == "helmet":
            color = (255, 0, 0)
        elif label == "vest":
            color = (0, 255, 255)

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(
            frame,
            label,
            (x1, max(y1 - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            2,
            cv2.LINE_AA,
        )


def draw_alerts(frame: np.ndarray, alerts: list[str]) -> None:
    if not alerts:
        return

    visible_alerts = alerts[:4]
    start_y = 30
    for index, alert in enumerate(visible_alerts):
        y = start_y + index * 28
        cv2.putText(
            frame,
            alert,
            (20, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2,
            cv2.LINE_AA,
        )


def main() -> None:
    args = parse_args()
    zones = load_zones(args.zones)
    logger = JsonlEventLogger(path=args.log_path)
    detector = YoloDetector(
        model_path=args.model,
        confidence_threshold=args.confidence,
        allowed_labels={"person", "helmet", "vest"},
    )

    capture = cv2.VideoCapture(parse_source(str(args.source)))
    if not capture.isOpened():
        raise RuntimeError(f"Could not open source: {args.source}")

    print("CCTV pipeline demo started. Press 'q' to exit.")

    try:
        while capture.isOpened():
            success, frame = capture.read()
            if not success:
                break

            detections = detector.predict_as_dicts(frame)
            result = process_frame(detections, zones, logger)

            annotated = draw_zones(frame.copy(), zones, result["events"])
            draw_detections(annotated, detections, result["ppe_results"], result["events"])
            draw_alerts(annotated, result["alerts"])

            cv2.imshow("SAEGIL CCTV Pipeline Demo", annotated)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        capture.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
