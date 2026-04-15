from __future__ import annotations

import json
import tempfile
from pathlib import Path

from fastapi.testclient import TestClient

from apps.backend import api
from apps.backend.config.settings import Settings
from apps.backend.main import app


def test_mock_inference_flow_creates_and_exposes_events(monkeypatch) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        log_path = temp_path / "events.jsonl"
        zone_path = temp_path / "zones.json"
        zone_path.write_text(
            json.dumps(
                [
                    {
                        "id": "zone-a",
                        "name": "test_zone",
                        "severity": "high",
                        "points": [[90, 90], [210, 90], [210, 310], [90, 310]],
                    }
                ],
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        def override_settings() -> Settings:
            return Settings(
                log_path=str(log_path),
                zone_path=str(zone_path),
                model_path="models/weights/stage1_best.pt",
            )

        monkeypatch.setattr(api.routes, "get_settings", override_settings)
        api.routes.get_detector.cache_clear()

        client = TestClient(app)

        infer_response = client.post(
            "/infer/image",
            json={
                "detector_mode": "mock",
                "mock_scenario": "zone_intrusion_missing_ppe",
                "zones": [
                    {
                        "id": "zone-a",
                        "name": "test_zone",
                        "severity": "high",
                        "points": [[90, 90], [210, 90], [210, 310], [90, 310]],
                    }
                ],
            },
        )

        assert infer_response.status_code == 200
        infer_payload = infer_response.json()
        assert len(infer_payload["events"]) == 3

        events_response = client.get("/events", params={"limit": 10})
        assert events_response.status_code == 200
        events_payload = events_response.json()
        assert len(events_payload["events"]) == 3

        event_types = {event["type"] for event in events_payload["events"]}
        assert event_types == {"zone_intrusion", "missing_helmet", "missing_vest"}

        event_id = events_payload["events"][0]["event_id"]
        detail_response = client.get(f"/events/{event_id}")
        assert detail_response.status_code == 200
        assert detail_response.json()["event"]["event_id"] == event_id

        zones_response = client.get("/zones")
        assert zones_response.status_code == 200
        assert zones_response.json()["zones"][0]["id"] == "zone-a"
