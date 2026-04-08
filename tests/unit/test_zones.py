from core.zones.polygon_zone import detect_zone_intrusions, point_in_polygon


def test_detect_zone_intrusions_returns_event_for_person_inside_zone() -> None:
    detections = [{"label": "person", "bbox": (120, 120, 180, 220), "track_id": 1}]
    zones = [{"id": "z1", "points": [(100, 100), (300, 100), (300, 300), (100, 300)]}]

    events = detect_zone_intrusions(detections, zones)

    assert len(events) == 1
    assert events[0]["type"] == "zone_intrusion"
    assert events[0]["track_id"] == 1


def test_detect_zone_intrusions_uses_foot_point_for_entry() -> None:
    detections = [{"label": "person", "bbox": (120, 20, 180, 120), "track_id": 3}]
    zones = [{"id": "z1", "points": [(100, 100), (300, 100), (300, 300), (100, 300)]}]

    events = detect_zone_intrusions(detections, zones)

    assert len(events) == 1
    assert events[0]["trigger_point"] == (150.0, 120.0)


def test_detect_zone_intrusions_returns_no_event_for_person_outside_zone() -> None:
    detections = [{"label": "person", "bbox": (10, 10, 50, 90), "track_id": 2}]
    zones = [{"id": "z1", "points": [(100, 100), (300, 100), (300, 300), (100, 300)]}]

    events = detect_zone_intrusions(detections, zones)

    assert events == []


def test_point_in_polygon_supports_non_rectangular_zone() -> None:
    polygon = [(100, 100), (200, 120), (180, 220), (120, 240), (80, 180)]

    assert point_in_polygon((140, 180), polygon) is True
    assert point_in_polygon((230, 180), polygon) is False
