from core.alerts.overlay import build_alert_messages
from core.logging.event_logger import JsonlEventLogger
from core.ppe.matcher import evaluate_ppe
from core.risk.rules import evaluate_risks
from core.zones.polygon_zone import detect_zone_intrusions


def process_frame(detections: list[dict], zones: list[dict], logger: JsonlEventLogger) -> dict:
    ppe_results = evaluate_ppe(detections)
    zone_events = detect_zone_intrusions(detections, zones)
    risk_events = evaluate_risks(detections, ppe_results, zone_events)

    events = zone_events + risk_events
    stored_events = logger.write_events(events)

    return {
        "ppe_results": ppe_results,
        "events": stored_events,
        "alerts": build_alert_messages(stored_events),
    }
