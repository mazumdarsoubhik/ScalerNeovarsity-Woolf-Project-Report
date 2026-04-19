from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.custom_logging import configure_logging, get_logger
from app.core.database import init_db

configure_logging()
logger = get_logger(__name__)

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="NutriFlow modular backend for meals, dashboard, and nutrition chat.",
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    logger.info("Application startup complete")


app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "NutriFlow backend is running"}
