from functools import lru_cache

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "construction-safety-system"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_path: str = "data/processed/events.jsonl"
    camera_source: str = "0"
    model_path: str = "models/weights/yolo.pt"


@lru_cache
def get_settings() -> Settings:
    return Settings()
