from core.alerts.overlay import build_alert_messages
from core.logging.event_logger import JsonlEventLogger
from core.ppe.matcher import evaluate_ppe
from core.risk.rules import evaluate_risks
from core.zones.polygon_zone import detect_zone_intrusions


def process_frame(detections: list[dict], zones: list[dict], logger: JsonlEventLogger) -> dict:
    # 한 프레임에 대해 PPE 판단, 구역 침입 판단, 위험 이벤트 생성을 순서대로 수행합니다.
    ppe_results = evaluate_ppe(detections)
    zone_events = detect_zone_intrusions(detections, zones)
    risk_events = evaluate_risks(detections, ppe_results, zone_events)

    # 발생한 이벤트는 로그에 저장한 뒤, 저장 결과 기준으로 알림 문구를 만듭니다.
    events = zone_events + risk_events
    stored_events = logger.write_events(events)

    return {
        "ppe_results": ppe_results,
        "events": stored_events,
        "alerts": build_alert_messages(stored_events),
    }
