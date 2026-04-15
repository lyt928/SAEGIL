from __future__ import annotations


DEFAULT_MOCK_SCENARIO = "zone_intrusion_missing_ppe"


def get_mock_detections(scenario: str = DEFAULT_MOCK_SCENARIO) -> list[dict]:
    normalized = scenario.strip().lower()

    scenarios: dict[str, list[dict]] = {
        "zone_intrusion_missing_ppe": [
            {
                "label": "person",
                "bbox": (100, 100, 200, 300),
                "track_id": 1,
                "confidence": 0.95,
            }
        ],
        "ppe_complete": [
            {
                "label": "person",
                "bbox": (100, 100, 200, 300),
                "track_id": 1,
                "confidence": 0.95,
            },
            {
                "label": "helmet",
                "bbox": (130, 105, 170, 145),
                "confidence": 0.92,
            },
            {
                "label": "vest",
                "bbox": (120, 160, 180, 240),
                "confidence": 0.93,
            },
        ],
        "two_workers_mixed": [
            {
                "label": "person",
                "bbox": (80, 100, 180, 300),
                "track_id": 1,
                "confidence": 0.95,
            },
            {
                "label": "person",
                "bbox": (240, 100, 340, 300),
                "track_id": 2,
                "confidence": 0.94,
            },
            {
                "label": "helmet",
                "bbox": (110, 105, 150, 145),
                "confidence": 0.91,
            },
            {
                "label": "vest",
                "bbox": (100, 160, 160, 240),
                "confidence": 0.9,
            },
        ],
    }

    return scenarios.get(normalized, scenarios[DEFAULT_MOCK_SCENARIO])
