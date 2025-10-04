import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
# from starlette.staticfiles import StaticFiles

from core.config import settings
from api.v1.main import app_v1
from api.v1.routes import health
from utils.common import CustomHTTPException
from utils.custom_logging import log

# Set the project root path
settings.project_root_path = os.path.dirname(os.path.abspath(__file__))

if settings.environment == 'production':
    app = FastAPI(
        title=settings.project_name,
        openapi_url=None,
        docs_url=None,
        redoc_url=None
    )
else:
    app = FastAPI(title=settings.project_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=settings.allowed_credentials,
    allow_methods=['*'],
    allow_headers=['*'],
)


def exception_handler(fast_app: FastAPI):
    """
        Exception handler for custom exceptions
    """

    @fast_app.exception_handler(CustomHTTPException)
    async def custom_http_exception_handler(_: Request, exc: CustomHTTPException):
        response = {
            'status': exc.status,
            'message': exc.message
        }
        return JSONResponse(status_code=exc.status_code, content=response)


exception_handler(app)
exception_handler(app_v1)

app.include_router(health.router, prefix='/health')

app.mount('/api/v1', app_v1)

# app.mount("/static", StaticFiles(directory="static"), name="static")


log.info("Project %s - %s Initialized", settings.project_name_short, settings.project_version)
