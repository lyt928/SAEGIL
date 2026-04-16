from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class JsonZoneStore:
    path: str

    def _target(self) -> Path:
        # zone JSON 파일이 위치할 디렉터리를 자동으로 준비합니다.
        target = Path(self.path)
        target.parent.mkdir(parents=True, exist_ok=True)
        return target

    def read_all(self) -> list[dict]:
        target = self._target()
        if not target.exists():
            return []
        return json.loads(target.read_text(encoding="utf-8-sig"))

    def write_all(self, zones: list[dict]) -> list[dict]:
        target = self._target()
        target.write_text(json.dumps(zones, ensure_ascii=False, indent=2), encoding="utf-8")
        return zones

    def read_one(self, zone_id: str) -> dict | None:
        for zone in self.read_all():
            if zone.get("id") == zone_id:
                return zone
        return None

    def upsert(self, zone: dict) -> dict:
        # zone id를 기준으로 기존 항목을 교체하거나 새 항목을 추가합니다.
        zones = self.read_all()
        updated = False
        for index, current in enumerate(zones):
            if current.get("id") == zone.get("id"):
                zones[index] = zone
                updated = True
                break

        if not updated:
            zones.append(zone)

        self.write_all(zones)
        return zone

    def delete(self, zone_id: str) -> bool:
        # 삭제 대상이 없으면 False를 반환해 API에서 404 처리할 수 있게 합니다.
        zones = self.read_all()
        remaining = [zone for zone in zones if zone.get("id") != zone_id]
        if len(remaining) == len(zones):
            return False
        self.write_all(remaining)
        return True
