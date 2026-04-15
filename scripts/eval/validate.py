import os
import sys
from pathlib import Path
from ultralytics import YOLO

# 프로젝트 루트를 경로에 추가
FILE = Path(__file__).resolve()
ROOT = FILE.parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from core.detection.model_paths import get_default_model_path

def validate_model():
    # 1. 모델 설정 (학습된 가중치 파일 경로를 넣기)
    model_path = get_default_model_path(FILE)
    model = YOLO(str(model_path))

    # 2. 데이터셋 설정
    # 공의 데이터셋 경로가 적힌 data.yaml 파일이 필요
    # 보통 data/datasets/ 폴더 안에
    data_yaml_path = ROOT / "data" / "datasets" / "aihub-construction-safety" / "data.yaml"

    # 3. 평가 수행 (Validation)
    # imgsz는 학습할 때 썼던 크기와 맞추는 것이 좋음 (보통 640)
    print("성능 평가를 시작하오. 데이터셋 규모에 따라 시간이 걸릴 수 있소.")
    results = model.val(data=str(data_yaml_path), imgsz=640, split='test')

    # 4. 주요 지표 출력
    print("-" * 30)
    print(f"평균 정밀도 (mAP50): {results.box.map50:.4f}")
    print(f"평균 정밀도 (mAP50-95): {results.box.map:.4f}")
    print(f"정밀도 (Precision): {results.box.mp:.4f}")
    print(f"재현율 (Recall): {results.box.mr:.4f}")
    print("-" * 30)
    
    # 상세 결과는 runs/detect/val 폴더에 저장

if __name__ == "__main__":
    validate_model()
