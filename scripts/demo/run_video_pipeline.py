from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

FILE = Path(__file__).resolve()
ROOT = FILE.parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from apps.backend.services.pipeline import process_frame
from core.camera.stream import CameraConfig, iter_frames, source_exists
from core.detection.mock_detector import DEFAULT_MOCK_SCENARIO, get_mock_detections
from core.detection.yolo_detector import YoloDetector
from core.logging.event_logger import JsonlEventLogger


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run frame-by-frame safety pipeline on camera or video input.")
    parser.add_argument("--source", default="0", help="Camera index or video file path")
    parser.add_argument("--mode", choices=("mock", "real"), default="mock", help="Detection mode")
    parser.add_argument("--mock-scenario", default=DEFAULT_MOCK_SCENARIO, help="Mock detection scenario name")
    parser.add_argument("--zones", default="data/samples/sample_zones.json", help="Zone JSON file path")
    parser.add_argument("--max-frames", type=int, default=30, help="Maximum number of frames to process")
    parser.add_argument("--log-path", default="data/processed/events.jsonl", help="Event log output path")
    parser.add_argument("--model-path", default="models/weights/stage1_best.pt", help="YOLO model path for real mode")
    return parser.parse_args()


def load_zones(path: str) -> list[dict]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_detector(mode: str, model_path: str) -> YoloDetector | None:
    if mode == "real":
        return YoloDetector(
            model_path=model_path,
            allowed_labels={"person", "helmet", "vest"},
        )
    return None


def main() -> int:
    args = parse_args()

    if not source_exists(args.source):
        print(f"입력 소스를 찾을 수 없습니다: {args.source}")
        return 1

    zones = load_zones(args.zones)
    logger = JsonlEventLogger(path=args.log_path)
    detector = build_detector(args.mode, args.model_path)
    config = CameraConfig(source=args.source)

    processed = 0
    total_events = 0

    for frame_index, frame in iter_frames(config, max_frames=args.max_frames):
        if args.mode == "mock":
            detections = get_mock_detections(args.mock_scenario)
        else:
            detections = detector.predict_as_dicts(frame) if detector is not None else []

        result = process_frame(detections=detections, zones=zones, logger=logger)
        processed += 1
        total_events += len(result["events"])

        print(
            json.dumps(
                {
                    "frame": frame_index,
                    "mode": args.mode,
                    "detections": len(detections),
                    "events": len(result["events"]),
                    "alerts": result["alerts"],
                },
                ensure_ascii=False,
            )
        )

    print(
        json.dumps(
            {
                "processed_frames": processed,
                "total_events": total_events,
                "log_path": args.log_path,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
