$env:RUN_MODE = "real"
$env:DETECTOR_MODE = "real"

python -m uvicorn apps.backend.main:app --reload --host 0.0.0.0 --port 8000
