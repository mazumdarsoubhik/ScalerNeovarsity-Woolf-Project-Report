from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.chat import router as chat_router
from app.api.v1.endpoints.dashboard import router as dashboard_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.meals import router as meals_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(meals_router)
api_router.include_router(dashboard_router)
api_router.include_router(chat_router)
