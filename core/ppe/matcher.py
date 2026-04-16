from __future__ import annotations


def _bbox_center(bbox: tuple[int, int, int, int]) -> tuple[float, float]:
    x1, y1, x2, y2 = bbox
    return ((x1 + x2) / 2, (y1 + y2) / 2)


def _point_in_box(point: tuple[float, float], bbox: tuple[int, int, int, int]) -> bool:
    x, y = point
    x1, y1, x2, y2 = bbox
    return x1 <= x <= x2 and y1 <= y <= y2


def _relative_position(point: tuple[float, float], bbox: tuple[int, int, int, int]) -> tuple[float, float]:
    # 사람 bbox 안에서의 상대 좌표를 구해 헬멧/조끼 위치 판정에 사용합니다.
    x, y = point
    x1, y1, x2, y2 = bbox
    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)
    return ((x - x1) / width, (y - y1) / height)


def _is_helmet_for_person(
    helmet_bbox: tuple[int, int, int, int],
    person_bbox: tuple[int, int, int, int],
) -> bool:
    # 헬멧 중심점이 사람 상단 영역에 있을 때만 착용으로 간주합니다.
    center = _bbox_center(helmet_bbox)
    if not _point_in_box(center, person_bbox):
        return False

    rel_x, rel_y = _relative_position(center, person_bbox)
    return 0.15 <= rel_x <= 0.85 and 0.0 <= rel_y <= 0.35


def _is_vest_for_person(
    vest_bbox: tuple[int, int, int, int],
    person_bbox: tuple[int, int, int, int],
) -> bool:
    # 조끼 중심점이 사람 몸통 영역에 있을 때만 착용으로 간주합니다.
    center = _bbox_center(vest_bbox)
    if not _point_in_box(center, person_bbox):
        return False

    rel_x, rel_y = _relative_position(center, person_bbox)
    return 0.15 <= rel_x <= 0.85 and 0.2 <= rel_y <= 0.75


def evaluate_ppe(detections: list[dict]) -> list[dict]:
    # 사람마다 연결된 헬멧/조끼가 있는지 계산해 PPE 결과를 만듭니다.
    people = [det for det in detections if det.get("label") == "person" and det.get("bbox")]
    helmets = [det for det in detections if det.get("label") == "helmet" and det.get("bbox")]
    vests = [det for det in detections if det.get("label") == "vest" and det.get("bbox")]

    results = []
    for person in people:
        person_bbox = person["bbox"]
        matched_helmets = [helmet for helmet in helmets if _is_helmet_for_person(helmet["bbox"], person_bbox)]
        matched_vests = [vest for vest in vests if _is_vest_for_person(vest["bbox"], person_bbox)]

        results.append(
            {
                "person_id": person.get("track_id"),
                "bbox": person_bbox,
                "has_helmet": bool(matched_helmets),
                "has_vest": bool(matched_vests),
                "matched_helmet": matched_helmets[0]["bbox"] if matched_helmets else None,
                "matched_vest": matched_vests[0]["bbox"] if matched_vests else None,
            }
        )
    return results
