from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from apps.backend.api.routes import router
from apps.backend.config.settings import get_settings


settings = get_settings()
app = FastAPI(title=settings.app_name)
app.include_router(router)

# 정적 대시보드를 `/dashboard` 경로로 노출합니다.
dashboard_dir = Path(__file__).resolve().parents[1] / "dashboard" / "public"
app.mount("/dashboard", StaticFiles(directory=dashboard_dir, html=True), name="dashboard")


@app.get("/")
def root() -> dict[str, str]:
    # 현재 실행 모드와 기본 설정을 빠르게 확인하기 위한 진입점입니다.
    return {
        "message": f"{settings.app_name} backend is running",
        "run_mode": settings.run_mode,
        "detector_mode": settings.detector_mode,
        "mock_scenario": settings.mock_scenario,
    }
