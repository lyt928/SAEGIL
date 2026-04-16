from __future__ import annotations

from pathlib import Path
from typing import Any

from core.detection.types import Detection


class YoloDetector:
    def __init__(
        self,
        model_path: str,
        confidence_threshold: float = 0.25,
        allowed_labels: set[str] | None = None,
    ) -> None:
        # 실제 모델 로드는 지연시키고, 설정만 먼저 저장합니다.
        self.model_path = Path(model_path)
        self.confidence_threshold = confidence_threshold
        self.allowed_labels = allowed_labels
        self._model: Any | None = None

    def load(self) -> None:
        # 첫 추론 시점에만 ultralytics YOLO 모델을 메모리에 올립니다.
        if self._model is not None:
            return
        if not self.model_path.exists():
            raise FileNotFoundError(f"YOLO model not found: {self.model_path}")

        try:
            from ultralytics import YOLO
        except ImportError as exc:
            raise RuntimeError("ultralytics is not installed. Install requirements first.") from exc

        self._model = YOLO(str(self.model_path))

    def predict(self, frame: object) -> list[Detection]:
        # 모델 추론 결과를 프로젝트 공통 Detection 형식으로 변환합니다.
        self.load()
        results = self._model.predict(frame, conf=self.confidence_threshold, verbose=False)
        detections: list[Detection] = []
        for result in results:
            detections.extend(self._parse_result(result))
        return detections

    def predict_as_dicts(self, frame: object) -> list[dict]:
        return [detection.__dict__ for detection in self.predict(frame)]

    def _parse_result(self, result: Any) -> list[Detection]:
        # YOLO 결과 객체에서 bbox, score, class, track 정보를 꺼내 정규화합니다.
        names = getattr(result, "names", {})
        boxes = getattr(result, "boxes", None)
        if boxes is None:
            return []

        xyxy_values = self._to_list(getattr(boxes, "xyxy", []))
        conf_values = self._to_list(getattr(boxes, "conf", []))
        cls_values = self._to_list(getattr(boxes, "cls", []))
        track_values = self._to_list(getattr(boxes, "id", [])) if getattr(boxes, "id", None) is not None else []

        detections: list[Detection] = []
        for index, bbox in enumerate(xyxy_values):
            confidence = float(conf_values[index]) if index < len(conf_values) else 0.0
            class_id = int(cls_values[index]) if index < len(cls_values) else -1
            raw_label = names.get(class_id, str(class_id))
            label = self._normalize_label(raw_label)

            if confidence < self.confidence_threshold:
                continue
            if self.allowed_labels is not None and label not in self.allowed_labels:
                continue

            track_id = None
            if index < len(track_values) and track_values[index] is not None:
                track_id = int(track_values[index])

            detections.append(
                Detection(
                    label=label,
                    confidence=confidence,
                    bbox=tuple(int(value) for value in bbox),
                    track_id=track_id,
                )
            )
        return detections

    @staticmethod
    def _normalize_label(label: str) -> str:
        # 데이터셋마다 다른 클래스 이름을 내부 공통 라벨로 맞춥니다.
        normalized = label.strip().lower().replace("-", "_").replace(" ", "_")
        aliases = {
            "hardhat": "helmet",
            "helmet_on": "helmet",
            "safety_helmet": "helmet",
            "safety_vest": "vest",
            "safety-vest": "vest",
            "reflective_vest": "vest",
            "worker": "person",
        }
        return aliases.get(normalized, normalized)

    @staticmethod
    def _to_list(values: Any) -> list:
        if values is None:
            return []
        if hasattr(values, "tolist"):
            return values.tolist()
        return list(values)
