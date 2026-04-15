from pathlib import Path
from uuid import uuid4

from core.logging.event_logger import JsonlEventLogger


def test_write_event_adds_metadata(tmp_path: Path) -> None:
    target = tmp_path / f"events-{uuid4()}.jsonl"
    logger = JsonlEventLogger(path=str(target))

    try:
        event = logger.write_event({"type": "zone_intrusion", "severity": "high"})

        assert event["type"] == "zone_intrusion"
        assert "event_id" in event
        assert "timestamp" in event
    finally:
        target.unlink(missing_ok=True)


def test_read_recent_events_returns_latest_first(tmp_path: Path) -> None:
    target = tmp_path / f"events-{uuid4()}.jsonl"
    logger = JsonlEventLogger(path=str(target))

    try:
        logger.write_event({"type": "first", "severity": "low"})
        logger.write_event({"type": "second", "severity": "high"})

        events = logger.read_recent_events(limit=2)

        assert len(events) == 2
        assert events[0]["type"] == "second"
        assert events[1]["type"] == "first"
    finally:
        target.unlink(missing_ok=True)
