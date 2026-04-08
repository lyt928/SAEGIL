def evaluate_risks(detections: list[dict], ppe_results: list[dict], zone_events: list[dict]) -> list[dict]:
    _ = detections
    _ = zone_events
    events = []
    for item in ppe_results:
        if not item["has_helmet"]:
            events.append(
                {
                    "type": "missing_helmet",
                    "severity": "medium",
                    "track_id": item.get("person_id"),
                }
            )
        if not item["has_vest"]:
            events.append(
                {
                    "type": "missing_vest",
                    "severity": "low",
                    "track_id": item.get("person_id"),
                }
            )
    return events
