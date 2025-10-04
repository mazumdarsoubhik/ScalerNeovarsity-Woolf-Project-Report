from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from core.config import settings
from utils.custom_logging import log

router = APIRouter()


@router.get('')
async def health() -> JSONResponse:
    """
        Health API to check if the server is running
    """

    response = {
        'status': 'success',
        'message': 'Server is up and running',
        'environment': settings.environment,
        'project_version': settings.project_version,
        'server_start_time': settings.server_start_time
    }

    log.info(response)

    return JSONResponse(status_code=status.HTTP_200_OK, content=response)