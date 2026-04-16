import os
from functools import lru_cache

from pydantic import BaseModel, ConfigDict
from core.detection.model_paths import DEFAULT_MODEL_RELATIVE_PATH


class Settings(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    # 환경변수가 없을 때 사용할 기본 실행 설정입니다.
    app_name: str = "construction-safety-system"
    run_mode: str = "dev"
    detector_mode: str = "real"
    mock_scenario: str = "zone_intrusion_missing_ppe"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_path: str = "data/processed/events.jsonl"
    zone_path: str = "data/samples/sample_zones.json"
    camera_source: str = "0"
    model_path: str = DEFAULT_MODEL_RELATIVE_PATH


@lru_cache
def get_settings() -> Settings:
    # 환경변수를 한 번만 읽고 재사용합니다.
    return Settings(
        app_name=os.getenv("APP_NAME", "construction-safety-system"),
        run_mode=os.getenv("RUN_MODE", "dev"),
        detector_mode=os.getenv("DETECTOR_MODE", "real"),
        mock_scenario=os.getenv("MOCK_SCENARIO", "zone_intrusion_missing_ppe"),
        api_host=os.getenv("API_HOST", "0.0.0.0"),
        api_port=int(os.getenv("API_PORT", "8000")),
        log_path=os.getenv("LOG_PATH", "data/processed/events.jsonl"),
        zone_path=os.getenv("ZONE_PATH", "data/samples/sample_zones.json"),
        camera_source=os.getenv("CAMERA_SOURCE", "0"),
        model_path=os.getenv("MODEL_PATH", DEFAULT_MODEL_RELATIVE_PATH),
    )
