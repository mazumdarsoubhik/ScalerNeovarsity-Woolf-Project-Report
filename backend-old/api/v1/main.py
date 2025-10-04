from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.routes import health
from core.config import settings
# from middleware.authenticator import AuthMiddleware

if settings.environment == 'production':
    app_v1 = FastAPI(
        title=settings.project_name,
        openapi_url=None,
        docs_url=None,
        redoc_url=None
    )
else:
    app_v1 = FastAPI(title=settings.project_name)

app_v1.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=settings.allowed_credentials,
    allow_methods=['*'],
    allow_headers=['*'],
)

app_v1.include_router(health.router, prefix='/health')


# app_v1.add_middleware(AuthMiddleware)
