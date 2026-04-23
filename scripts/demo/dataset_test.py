import cv2
import numpy as np
from ultralytics import YOLO
import sys
from pathlib import Path

# 1. 프로젝트 루트 경로 설정
FILE = Path(__file__).resolve()
# 프로젝트 루트를 기준으로 모델과 core 모듈 경로를 맞춥니다.
ROOT = FILE.parents[2] 
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

# 동료 파일 이름에 맞춰 수입
from core.detection.model_paths import get_default_model_path

try:
    from core.zones.polygon_zone import detect_zone_intrusions, detection_foot_point
except ImportError:
    from core.zones.polygon import detect_zone_intrusions, detection_foot_point

def run_full_dataset_red_test():
    # 데이터셋 전체 이미지를 돌면서 구역 침입 결과를 시각화합니다.
    # 모델 및 경로 설정
    model_path = get_default_model_path(FILE)
    model = YOLO(str(model_path))

    # 결과 저장 폴더 (data/samples 활용)
    output_dir = ROOT / "data" / "samples"

    # 테스트 데이터셋 경로 (AIHub)
    dataset_dir = ROOT / "data" / "datasets" / "aihub-construction-safety"
    
    # 이미지 파일 수색 
    image_paths = list(dataset_dir.rglob("*.jpg")) + list(dataset_dir.rglob("*.jpeg")) + list(dataset_dir.rglob("*.png"))

    if not image_paths:
        print(f"그림을 찾을 수 없소: {dataset_dir}")
        return

    # 3. 시연용 확대 위험 구역 설정
    # 발끝이 확실히 걸리도록 아래쪽 Y좌표를 1000까지 넉넉히 
    zones = [{
        "id": "demo_red_zone",
        "name": "발표 시연용 위험 구역",
        "points": [[100, 300], [540, 300], [800, 1000], [20, 1000]],
        "severity": "high"
    }]

    total = len(image_paths)
    print(f"총 {total}장의 그림을 모두 분석하여 {output_dir}에 저장.")

    for i, img_path in enumerate(image_paths):
        frame = cv2.imread(str(img_path))
        if frame is None: continue

        # YOLO 추론
        results = model(frame, verbose=False)
        
        # 사람 detection만 남겨서 구역 판정에 사용합니다.
        detections = []
        for box in results[0].boxes:
            if int(box.cls[0]) == 0: # 사람
                detections.append({
                    "label": "person",
                    "bbox": box.xyxy[0].cpu().numpy().astype(int).tolist(),
                    "conf": float(box.conf[0])
                })

        # 침범 판정 가동
        intrusions = detect_zone_intrusions(detections, zones)

        # 결과 시각화
        # 결과 이미지는 발표용으로 바로 볼 수 있게 저장합니다.
        overlay = frame.copy()
        for zone in zones:
            pts = np.array(zone["points"], np.int32)
            is_warn = any(i["zone_id"] == zone["id"] for i in intrusions)
            color = (0, 0, 255) if is_warn else (0, 255, 0)
            cv2.polylines(frame, [pts], True, color, 3)
            cv2.fillPoly(overlay, [pts], color)
        
        frame = cv2.addWeighted(overlay, 0.3, frame, 0.7, 0)

        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            foot = detection_foot_point(det["bbox"])
            is_in = any(i["person_bbox"] == det["bbox"] for i in intrusions)
            c = (0, 0, 255) if is_in else (0, 255, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), c, 2)
            cv2.circle(frame, (int(foot[0]), int(foot[1])), 6, c, -1)

        # 저장 파일명을 원본 파일명을 포함하여 생성
        save_name = f"res_red_all_{img_path.stem}.jpg"
        save_path = output_dir / save_name
        cv2.imwrite(str(save_path), frame)
        
        # 진행 상황 표시
        if (i + 1) % 10 == 0 or (i + 1) == total:
            print(f"현황: {i+1}/{total} 완료...")

    print(f"모든 결과가 {output_dir}에 저장. 이제 발표 준비")

if __name__ == "__main__":
    run_full_dataset_red_test()
