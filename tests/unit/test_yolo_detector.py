from pathlib import Path

from core.detection.yolo_detector import YoloDetector


class FakeArray:
    def __init__(self, values):
        self._values = values

    def tolist(self):
        return self._values


class FakeBoxes:
    def __init__(self, xyxy, conf, cls, track_ids=None):
        self.xyxy = FakeArray(xyxy)
        self.conf = FakeArray(conf)
        self.cls = FakeArray(cls)
        self.id = FakeArray(track_ids) if track_ids is not None else None


class FakeResult:
    def __init__(self, names, boxes):
        self.names = names
        self.boxes = boxes


def test_parse_result_normalizes_labels_and_tracks_ids() -> None:
    detector = YoloDetector(model_path="models/weights/yolo.pt", allowed_labels={"person", "helmet", "vest"})
    result = FakeResult(
        names={0: "Person", 1: "Hardhat", 2: "safety vest"},
        boxes=FakeBoxes(
            xyxy=[[10, 20, 30, 40], [15, 25, 35, 45], [20, 30, 40, 60]],
            conf=[0.9, 0.8, 0.85],
            cls=[0, 1, 2],
            track_ids=[101, 102, 103],
        ),
    )

    detections = detector._parse_result(result)

    assert [item.label for item in detections] == ["person", "helmet", "safety_vest"]
    assert detections[0].track_id == 101


def test_parse_result_filters_low_confidence_and_disallowed_labels() -> None:
    detector = YoloDetector(model_path="models/weights/yolo.pt", confidence_threshold=0.5, allowed_labels={"person"})
    result = FakeResult(
        names={0: "person", 1: "helmet"},
        boxes=FakeBoxes(
            xyxy=[[0, 0, 10, 10], [10, 10, 20, 20], [20, 20, 30, 30]],
            conf=[0.7, 0.9, 0.2],
            cls=[0, 1, 0],
        ),
    )

    detections = detector._parse_result(result)

    assert len(detections) == 1
    assert detections[0].label == "person"


def test_load_raises_when_model_file_is_missing() -> None:
    detector = YoloDetector(model_path=str(Path("models/weights/missing.pt")))

    try:
        detector.load()
    except FileNotFoundError:
        assert True
    else:
        assert False
