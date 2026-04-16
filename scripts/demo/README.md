# 데모 스크립트 안내

- `run_backend.ps1`: 실행 모드를 선택해 FastAPI 개발 서버 실행
- `run_backend_mock.ps1`: mock 탐지 기반 데모 서버 실행
- `run_backend_real.ps1`: 실제 모델 추론 기반 서버 실행
- `run_video_pipeline.py`: 카메라 또는 영상 파일을 프레임 단위로 처리하는 데모 스크립트

## 예시

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\demo\run_backend.ps1 -Mode demo
```

```powershell
python .\scripts\demo\run_video_pipeline.py --source 0 --mode mock --max-frames 30
```
