from fastapi import FastAPI

from apps.backend.api.routes import router
from apps.backend.config.settings import get_settings


settings = get_settings()
app = FastAPI(title=settings.app_name)
app.include_router(router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": f"{settings.app_name} backend is running"}
