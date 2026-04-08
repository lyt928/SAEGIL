from dataclasses import dataclass


@dataclass
class Detection:
    label: str
    confidence: float
    bbox: tuple[int, int, int, int]
    track_id: int | None = None
