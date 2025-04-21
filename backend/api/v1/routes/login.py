import traceback
from datetime import datetime
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi import status as http_status
from auth import auth
from auth.auth import decode_ad_access_token
from core.config import settings
from core.database_manager import db
from models import schemas
from models.models import User
from utils.common import unauthorized_message, custom_message, system_error_message
from utils.custom_logging import log
from utils.helpers import dict_to_str, str_to_dict, generate_uuid

router = APIRouter()


@router.post('/basic')
async def login_basic(user_details: schemas.UserLoginBasic) -> JSONResponse:
    """
        Login using username and password
    """
    try:

        if not settings.authentication_basic_enabled:
            log.error("Basic authentication is not enabled in the environment settings")
            return custom_message("error", "Service Unavailable", 503)

        with db.create_session() as db_session:
            user = db_session.query(User).filter(User.username == user_details.username).first()

            if user is None:
                return custom_message("error", "Invalid username/password provided", 401)

            if user.authentication_mode.lower() != "basic":
                return custom_message("error", "Invalid login type. Use the login type used while account creation", 405)

            if not user.active:
                return custom_message("error", "User Locked. Please contact admin", 401)

            if not auth.verify_password(user_details.password, user.password):
                user.invalid_login_attempts += 1
                db_session.commit()
                if user.invalid_login_attempts >= settings.basic_authentication_max_invalid_login_attempts:
                    user.active = False
                    return custom_message("error", "User Locked. Please contact admin", 401)

                return custom_message("error", "Invalid username/password provided", 401)

            user.invalid_login_attempts = 0
            user.last_login_timestamp = datetime.utcnow()
            db_session.commit()
            db_session.refresh(user)
            access_token, expiry_unix = auth.create_access_token(data={
                "unique_name": user.username,
            })

            refresh_token = auth.create_refresh_token(data={
                "unique_name": user.username
            })

            response = custom_message("success", "Login Successful", 200)
            response.set_cookie(key="access_token", value=access_token, httponly=settings.environment != "local", secure=settings.environment != "local")
            response.set_cookie(key="refresh_token", value=refresh_token, httponly=settings.environment != "local", secure=settings.environment != "local")
            response.set_cookie(key="access_token_exp", value=str(expiry_unix), httponly=False, secure=settings.environment != "local")
            return response
    except Exception as exception:
        log.error('Error: %s', exception)
        log.error(traceback.format_exc())
        return system_error_message()