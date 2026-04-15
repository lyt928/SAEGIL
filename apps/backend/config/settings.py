from functools import lru_cache

from pydantic import BaseModel, ConfigDict
from core.detection.model_paths import DEFAULT_MODEL_RELATIVE_PATH


class Settings(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    app_name: str = "construction-safety-system"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_path: str = "data/processed/events.jsonl"
    camera_source: str = "0"
    model_path: str = DEFAULT_MODEL_RELATIVE_PATH


@lru_cache
def get_settings() -> Settings:
    return Settings()
