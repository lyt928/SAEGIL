from __future__ import annotations


def detection_center(bbox: tuple[int, int, int, int]) -> tuple[float, float]:
    x1, y1, x2, y2 = bbox
    return ((x1 + x2) / 2, (y1 + y2) / 2)


def detection_foot_point(bbox: tuple[int, int, int, int]) -> tuple[float, float]:
    x1, _, x2, y2 = bbox
    return ((x1 + x2) / 2, float(y2))


def point_in_polygon(point: tuple[float, float], polygon: list[tuple[float, float]]) -> bool:
    if len(polygon) < 3:
        return False

    x, y = point
    inside = False
    j = len(polygon) - 1

    for i in range(len(polygon)):
        xi, yi = polygon[i]
        xj, yj = polygon[j]

        intersects = ((yi > y) != (yj > y)) and (
            x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-9) + xi
        )
        if intersects:
            inside = not inside
        j = i

    return inside


def normalize_zone_points(zone: dict) -> list[tuple[float, float]]:
    return [tuple(point) for point in zone.get("points", [])]


def detect_zone_intrusions(detections: list[dict], zones: list[dict]) -> list[dict]:
    events = []
    for det in detections:
        if det.get("label") != "person" or not det.get("bbox"):
            continue

        foot_point = detection_foot_point(det["bbox"])
        for zone in zones:
            polygon = normalize_zone_points(zone)
            if point_in_polygon(foot_point, polygon):
                events.append(
                    {
                        "type": "zone_intrusion",
                        "severity": zone.get("severity", "high"),
                        "zone_id": zone["id"],
                        "zone_name": zone.get("name", zone["id"]),
                        "track_id": det.get("track_id"),
                        "person_bbox": det["bbox"],
                        "trigger_point": foot_point,
                    }
                )
    return events
