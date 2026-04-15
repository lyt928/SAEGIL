from __future__ import annotations

from pathlib import Path


DEFAULT_MODEL_RELATIVE_PATH = "models/weights/stage1_best.pt"


def get_project_root(start: Path | None = None) -> Path:
    if start is None:
        start = Path(__file__).resolve()
    return start.parents[2]


def get_default_model_path(start: Path | None = None) -> Path:
    return get_project_root(start) / DEFAULT_MODEL_RELATIVE_PATH
