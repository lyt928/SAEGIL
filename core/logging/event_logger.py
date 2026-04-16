import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


@dataclass
class JsonlEventLogger:
    path: str

    def _target(self) -> Path:
        target = Path(self.path)
        target.parent.mkdir(parents=True, exist_ok=True)
        return target

    def prepare_event(self, event: dict) -> dict:
        prepared = dict(event)
        prepared.setdefault("event_id", str(uuid4()))
        prepared.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
        return prepared

    def write_event(self, event: dict) -> dict:
        prepared = self.prepare_event(event)
        target = self._target()
        with target.open("a", encoding="utf-8") as file:
            file.write(json.dumps(prepared, ensure_ascii=False) + "\n")
        return prepared

    def write_events(self, events: list[dict]) -> list[dict]:
        stored_events = []
        for event in events:
            stored_events.append(self.write_event(event))
        return stored_events

    def read_all_events(self) -> list[dict]:
        target = self._target()
        if not target.exists():
            return []

        with target.open("r", encoding="utf-8") as file:
            lines = file.readlines()

        return [json.loads(line) for line in lines if line.strip()]

    def read_recent_events(self, limit: int = 50) -> list[dict]:
        events = self.read_all_events()
        return list(reversed(events[-limit:]))

    def read_event(self, event_id: str) -> dict | None:
        for event in reversed(self.read_all_events()):
            if event.get("event_id") == event_id:
                return event
        return None

    def clear(self) -> None:
        target = self._target()
        if target.exists():
            target.unlink()
