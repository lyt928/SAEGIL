$env:RUN_MODE = "demo"
$env:DETECTOR_MODE = "mock"
$env:MOCK_SCENARIO = "zone_intrusion_missing_ppe"

python -m uvicorn apps.backend.main:app --reload --host 0.0.0.0 --port 8000
