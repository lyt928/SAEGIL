from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import cv2


@dataclass
class CameraConfig:
    source: int | str = 0
    width: int = 1280
    height: int = 720
    fps: int = 30


def describe_camera(config: CameraConfig) -> dict:
    return {
        "source": config.source,
        "width": config.width,
        "height": config.height,
        "fps": config.fps,
    }


def normalize_source(source: int | str) -> int | str:
    if isinstance(source, int):
        return source

    stripped = str(source).strip()
    if stripped.isdigit():
        return int(stripped)
    return stripped


def open_capture(config: CameraConfig) -> cv2.VideoCapture:
    source = normalize_source(config.source)
    capture = cv2.VideoCapture(source)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, config.width)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, config.height)
    capture.set(cv2.CAP_PROP_FPS, config.fps)
    return capture


def iter_frames(config: CameraConfig, max_frames: int | None = None) -> Iterator[tuple[int, object]]:
    capture = open_capture(config)
    if not capture.isOpened():
        raise RuntimeError(f"Unable to open camera/video source: {config.source}")

    frame_index = 0
    try:
        while True:
            success, frame = capture.read()
            if not success:
                break

            yield frame_index, frame
            frame_index += 1

            if max_frames is not None and frame_index >= max_frames:
                break
    finally:
        capture.release()


def source_exists(source: int | str) -> bool:
    normalized = normalize_source(source)
    if isinstance(normalized, int):
        return True
    return Path(normalized).exists()
