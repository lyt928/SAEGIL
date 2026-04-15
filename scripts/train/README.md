# 학습 스크립트 안내

- `helmet_stage1.ipynb`: 기존 실험 노트북
- `run_training.py`: 학습 실행 후 실험 로그와 메트릭을 `reports/experiments/<run_id>/`에 저장

예시:

```powershell
python scripts\train\run_training.py --data path\to\data.yaml --epochs 30 --imgsz 640
```
