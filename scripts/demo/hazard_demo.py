import cv2
import numpy as np
from ultralytics import YOLO
import sys
import os

# 프로젝트 루트를 경로에 추가하여 core 폴더의 코드 읽음
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

# 동료의 파일 이름에 맞게 수정
# 여기서는 core/zones/polygon_zone.py에 해당 함수들이 있다고 가정
from core.zones.polygon_zone import detect_zone_intrusions, detection_foot_point

def run_demo():
    # 1. 모델 설정 (무게중심 폴더 경로 활용)
    model = YOLO("../../models/weights/yolov8n.pt")
    cap = cv2.VideoCapture(0)

    # 2. 테스트용 구역 데이터 (동료의 코드 형식에 맞춤)
    # severity와 id 등 원래 정한 규격에 맞춤 
    zones = [
        {
            "id": "danger_area_1",
            "name": "굴착기 회전 반경",
            "points": [[100, 300], [540, 300], [600, 480], [40, 480]],
            "severity": "high"
        }
    ]

    print("SAEGIL 실전 데모를 시작. 'q'를 눌러 마치기.")

    while cap.isOpened():
        success, frame = cap.read()
        if not success: break

        # YOLO 탐지 실행
        results = model(frame, verbose=False)
        
        # 동료의 함수가 기대하는 detections 형식으로 변환
        current_detections = []
        for box in results[0].boxes:
            cls = int(box.cls[0])
            if cls == 0: # 사람인 경우만
                current_detections.append({
                    "label": "person",
                    "bbox": box.xyxy[0].cpu().numpy().astype(int).tolist(),
                    "conf": float(box.conf[0])
                })

        # 3. 침범 판정 로직 가동 (핵심 함수!)
        # 이 함수 하나로 모든 사람과 구역의 침범 여부를 판단
        intrusions = detect_zone_intrusions(current_detections, zones)

        # 4. 시각화 (화면에 결과를 그리기)
        # 구역 그리기
        for zone in zones:
            pts = np.array(zone["points"], np.int32)
            color = (0, 0, 255) if any(i["zone_id"] == zone["id"] for i in intrusions) else (0, 255, 0)
            cv2.polylines(frame, [pts], True, color, 2)
            
            # 반투명 채우기 효과
            overlay = frame.copy()
            cv2.fillPoly(overlay, [pts], color)
            frame = cv2.addWeighted(overlay, 0.3, frame, 0.7, 0)

        # 탐지된 사람 상자 그리기
        for det in current_detections:
            x1, y1, x2, y2 = det["bbox"]
            foot = detection_foot_point(det["bbox"])
            
            # 침범 여부에 따른 색상 변경
            is_warn = any(i["person_bbox"] == det["bbox"] for i in intrusions)
            box_color = (0, 0, 255) if is_warn else (0, 255, 0)
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)
            cv2.circle(frame, (int(foot[0]), int(foot[1])), 5, box_color, -1)

        cv2.imshow('SAEGIL - Integrated Safety System', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_demo()