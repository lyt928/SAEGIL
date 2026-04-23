def build_alert_messages(events: list[dict]) -> list[str]:
    # 내부 이벤트 타입을 사용자에게 보여줄 경고 문구로 바꿉니다.
    messages = []
    for event in events:
        if event["type"] == "zone_intrusion":
            zone_name = event.get("zone_name")
            if zone_name:
                messages.append(f"위험구역 침입 감지: {zone_name}")
            else:
                messages.append("위험구역 침입 감지")
        elif event["type"] == "missing_helmet":
            messages.append("안전모 미착용 감지")
        elif event["type"] == "missing_vest":
            messages.append("안전조끼 미착용 감지")
    return messages
