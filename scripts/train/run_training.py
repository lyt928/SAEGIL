from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


FILE = Path(__file__).resolve()
ROOT = FILE.parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from ultralytics import YOLO

from core.detection.model_paths import DEFAULT_MODEL_RELATIVE_PATH


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run YOLO training and store experiment artifacts.")
    parser.add_argument("--model", default="yolo11n.pt", help="Base YOLO model name or path.")
    parser.add_argument("--data", required=True, help="Path to the dataset YAML file.")
    parser.add_argument("--epochs", type=int, default=30, help="Number of training epochs.")
    parser.add_argument("--imgsz", type=int, default=640, help="Training image size.")
    parser.add_argument("--batch", type=int, default=16, help="Batch size.")
    parser.add_argument("--device", default=None, help="Training device, for example 0 or cpu.")
    parser.add_argument("--workers", type=int, default=8, help="Number of dataloader workers.")
    parser.add_argument(
        "--project",
        default=str(ROOT / "reports" / "ultralytics-runs"),
        help="Ultralytics training output directory.",
    )
    parser.add_argument("--name", default=None, help="Optional Ultralytics run name.")
    parser.add_argument(
        "--experiment-dir",
        default=str(ROOT / "reports" / "experiments"),
        help="Directory where experiment summaries will be stored.",
    )
    parser.add_argument(
        "--copy-best-to-default",
        action="store_true",
        help=f"Copy the best model to {DEFAULT_MODEL_RELATIVE_PATH} after training.",
    )
    return parser.parse_args()


def make_run_id(prefix: str = "train") -> str:
    return f"{datetime.now().strftime('%Y-%m-%d-%H%M%S')}-{prefix}"


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def normalize_float(value: Any) -> float | None:
    try:
        return round(float(value), 6)
    except (TypeError, ValueError):
        return None


def collect_overall_metrics(results: Any) -> dict[str, float | None]:
    box = getattr(results, "box", None)
    if box is None:
        return {}
    return {
        "precision": normalize_float(getattr(box, "mp", None)),
        "recall": normalize_float(getattr(box, "mr", None)),
        "map50": normalize_float(getattr(box, "map50", None)),
        "map50_95": normalize_float(getattr(box, "map", None)),
    }


def collect_class_metrics(results: Any) -> list[dict[str, float | str | None]]:
    box = getattr(results, "box", None)
    names = getattr(results, "names", {}) or {}
    class_indices = getattr(results, "ap_class_index", []) or []
    rows: list[dict[str, float | str | None]] = []

    if box is None:
        return rows

    for class_index in class_indices:
        precision, recall, map50, map50_95 = box.class_result(int(class_index))
        rows.append(
            {
                "class_id": int(class_index),
                "class_name": names.get(int(class_index), str(class_index)),
                "precision": normalize_float(precision),
                "recall": normalize_float(recall),
                "map50": normalize_float(map50),
                "map50_95": normalize_float(map50_95),
            }
        )
    return rows


def copy_if_exists(source: Path, destination: Path) -> str | None:
    if not source.exists():
        return None
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return str(destination)


def write_json(path: Path, payload: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def main() -> None:
    args = parse_args()
    run_id = args.name or make_run_id("training")
    experiment_root = ensure_directory(Path(args.experiment_dir))
    experiment_dir = ensure_directory(experiment_root / run_id)

    model = YOLO(args.model)
    train_kwargs = {
        "data": str(Path(args.data)),
        "epochs": args.epochs,
        "imgsz": args.imgsz,
        "batch": args.batch,
        "workers": args.workers,
        "project": str(Path(args.project)),
        "name": run_id,
        "exist_ok": True,
    }
    if args.device is not None:
        train_kwargs["device"] = args.device

    started_at = datetime.now().astimezone().isoformat()
    train_results = model.train(**train_kwargs)
    finished_at = datetime.now().astimezone().isoformat()

    val_results = model.val(data=str(Path(args.data)), imgsz=args.imgsz)

    train_save_dir = Path(getattr(train_results, "save_dir", Path(args.project) / run_id))
    best_model_path = train_save_dir / "weights" / "best.pt"
    last_model_path = train_save_dir / "weights" / "last.pt"

    metadata = {
        "run_id": run_id,
        "started_at": started_at,
        "finished_at": finished_at,
        "model": args.model,
        "data": str(Path(args.data)),
        "epochs": args.epochs,
        "imgsz": args.imgsz,
        "batch": args.batch,
        "device": args.device,
        "workers": args.workers,
        "train_save_dir": str(train_save_dir),
        "best_model_path": str(best_model_path) if best_model_path.exists() else None,
        "last_model_path": str(last_model_path) if last_model_path.exists() else None,
    }

    copied_best_path = copy_if_exists(best_model_path, experiment_dir / "best.pt")
    copy_if_exists(last_model_path, experiment_dir / "last.pt")
    copy_if_exists(train_save_dir / "results.png", experiment_dir / "results.png")
    copy_if_exists(train_save_dir / "confusion_matrix.png", experiment_dir / "confusion_matrix.png")
    copy_if_exists(train_save_dir / "confusion_matrix_normalized.png", experiment_dir / "confusion_matrix_normalized.png")
    copy_if_exists(train_save_dir / "F1_curve.png", experiment_dir / "F1_curve.png")
    copy_if_exists(train_save_dir / "P_curve.png", experiment_dir / "P_curve.png")
    copy_if_exists(train_save_dir / "R_curve.png", experiment_dir / "R_curve.png")
    copy_if_exists(train_save_dir / "PR_curve.png", experiment_dir / "PR_curve.png")

    if args.copy_best_to_default and copied_best_path is not None:
        default_model_target = ROOT / DEFAULT_MODEL_RELATIVE_PATH
        default_model_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(experiment_dir / "best.pt", default_model_target)
        metadata["copied_to_default_model_path"] = str(default_model_target)

    write_json(experiment_dir / "metadata.json", metadata)
    write_json(experiment_dir / "metrics.json", collect_overall_metrics(val_results))
    write_json(experiment_dir / "class_metrics.json", collect_class_metrics(val_results))

    print(f"Training completed: {run_id}")
    print(f"Experiment summary saved to: {experiment_dir}")
    if copied_best_path:
        print(f"Best model snapshot: {copied_best_path}")


if __name__ == "__main__":
    main()
