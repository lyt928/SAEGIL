from core.ppe.matcher import evaluate_ppe


def test_evaluate_ppe_marks_missing_items_when_not_detected() -> None:
    detections = [{"label": "person", "bbox": (0, 0, 10, 10), "track_id": 7}]

    result = evaluate_ppe(detections)

    assert result[0]["has_helmet"] is False
    assert result[0]["has_vest"] is False


def test_evaluate_ppe_matches_helmet_and_vest_inside_person_bbox() -> None:
    detections = [
        {"label": "person", "bbox": (100, 100, 200, 300), "track_id": 1},
        {"label": "helmet", "bbox": (130, 105, 170, 145)},
        {"label": "vest", "bbox": (120, 160, 180, 240)},
    ]

    result = evaluate_ppe(detections)

    assert result[0]["has_helmet"] is True
    assert result[0]["has_vest"] is True


def test_evaluate_ppe_does_not_match_other_persons_equipment() -> None:
    detections = [
        {"label": "person", "bbox": (0, 0, 100, 200), "track_id": 1},
        {"label": "person", "bbox": (200, 0, 300, 200), "track_id": 2},
        {"label": "helmet", "bbox": (225, 10, 265, 45)},
        {"label": "vest", "bbox": (220, 70, 280, 150)},
    ]

    result = evaluate_ppe(detections)

    assert result[0]["has_helmet"] is False
    assert result[0]["has_vest"] is False
    assert result[1]["has_helmet"] is True
    assert result[1]["has_vest"] is True


def test_evaluate_ppe_rejects_helmet_outside_head_region() -> None:
    detections = [
        {"label": "person", "bbox": (100, 100, 200, 300), "track_id": 3},
        {"label": "helmet", "bbox": (130, 220, 170, 260)},
    ]

    result = evaluate_ppe(detections)

    assert result[0]["has_helmet"] is False
