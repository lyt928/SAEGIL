from __future__ import annotations

from pathlib import Path


DEFAULT_MODEL_RELATIVE_PATH = "models/weights/stage1_best.pt"


def get_project_root(start: Path | None = None) -> Path:
    # 현재 파일 위치를 기준으로 프로젝트 루트를 계산합니다.
    if start is None:
        start = Path(__file__).resolve()
    return start.parents[2]


def get_default_model_path(start: Path | None = None) -> Path:
    # 기본 모델 상대 경로를 실제 절대 경로로 변환합니다.
    return get_project_root(start) / DEFAULT_MODEL_RELATIVE_PATH
