from dataclasses import dataclass


@dataclass
class Detection:
    # 모델 출력과 규칙 로직 사이에서 공통으로 쓰는 detection 형식입니다.
    label: str
    confidence: float
    bbox: tuple[int, int, int, int]
    track_id: int | None = None
