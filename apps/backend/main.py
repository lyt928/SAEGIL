from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from apps.backend.api.routes import router
from apps.backend.config.settings import get_settings


settings = get_settings()
app = FastAPI(title=settings.app_name)
app.include_router(router)

dashboard_dir = Path(__file__).resolve().parents[1] / "dashboard" / "public"
app.mount("/dashboard", StaticFiles(directory=dashboard_dir, html=True), name="dashboard")


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": f"{settings.app_name} backend is running",
        "run_mode": settings.run_mode,
        "detector_mode": settings.detector_mode,
        "mock_scenario": settings.mock_scenario,
    }
