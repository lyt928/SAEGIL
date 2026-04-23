from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import cv2


@dataclass
class CameraConfig:
    # 카메라 번호 또는 영상 파일 경로와 캡처 설정을 함께 묶습니다.
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
    # "0" 같은 문자열 입력도 실제 카메라 인덱스로 해석합니다.
    if isinstance(source, int):
        return source

    stripped = str(source).strip()
    if stripped.isdigit():
        return int(stripped)
    return stripped


def open_capture(config: CameraConfig) -> cv2.VideoCapture:
    # OpenCV 캡처를 열고 기본 해상도/FPS를 적용합니다.
    source = normalize_source(config.source)
    capture = cv2.VideoCapture(source)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, config.width)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, config.height)
    capture.set(cv2.CAP_PROP_FPS, config.fps)
    return capture


def iter_frames(config: CameraConfig, max_frames: int | None = None) -> Iterator[tuple[int, object]]:
    # 프레임 인덱스와 실제 프레임을 함께 순회할 수 있게 해줍니다.
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
    # 숫자 입력은 카메라 인덱스로 보고, 문자열 경로는 파일 존재 여부를 확인합니다.
    normalized = normalize_source(source)
    if isinstance(normalized, int):
        return True
    return Path(normalized).exists()
