# import time
# import traceback
#
# from fastapi import Request,Response
# from starlette.middleware.base import BaseHTTPMiddleware
# from auth import auth
# from auth.rbac import get_current_user
# from core.config import settings
# from utils.common import unauthorized_message
# from utils.custom_logging import log
# from middleware.context import current_username, current_ip
#
#
# def add_security_headers(response: Response) -> Response:
#     """
#     Add security headers to the response to mitigate spoofing, XSS, and other attacks.
#     """
#     # Add Content Security Policy (CSP) to prevent resource loading from untrusted sources
#     response.headers['Content-Security-Policy'] = "default-src 'self';"
#     # Set Cache-Control headers to disable caching and enhance security
#     response.headers['Cache-Control'] = "no-cache, no-store, max-age=0, must-revalidate"
#     # Prevent sniffing of content types
#     response.headers['X-Content-Type-Options'] = "nosniff"
#     # Enforce HTTPS connections (HSTS) for one year, including all subdomains
#     response.headers['Strict-Transport-Security'] = "max-age=31536000; includeSubDomains"
#
#     return response
#
#
# class AuthMiddleware(BaseHTTPMiddleware):
#     """
#         Class to validate auth token before each request
#     """
#     white_listed_url = [
#         '/health',
#         '/login/basic',
#         '/login/ad/auth-url',
#         '/login/ad/token',
#         '/token/refresh',
#         '/teams'
#     ]
#
#     async def get_response(self, request, call_next):
#         """
#             Function to forward the request to api and return response
#         """
#         # Set current user
#         user = get_current_user(request)
#         if user:
#             current_username.set(user)
#
#         client_host = request.client.host
#         current_ip.set(client_host)
#
#         request_api_path = request.url.path
#         request_api_method = request.method
#         log.info(request_api_method + " " + request_api_path)
#
#         response = await call_next(request)
#         log.info("%s %s - %s", request_api_method, request_api_path, str(response.status_code))
#         return response
#
#     async def dispatch(self, request: Request, call_next):
#         """
#             Dispatch method to process each request.
#         """
#         # ignore whitelisted url from token validation
#         for part_url in self.white_listed_url:
#             if part_url in str(request.url):
#                 response = await self.get_response(request, call_next)
#                 return add_security_headers(response)
#         # get token from cookies
#         access_token = request.cookies.get('access_token')
#         refresh_token = request.cookies.get('refresh_token')
#         # if auth token not present
#         if access_token is None or refresh_token is None:
#             # return unauthorized message
#             response = unauthorized_message()
#             return add_security_headers(response)
#
#         try:
#
#             if settings.authentication_basic_enabled:
#                 # Validate access token
#                 decoded_token = auth.decode_token(access_token)
#                 if decoded_token is None:
#                     if settings.authentication_ad_enabled:
#                         decoded_token = auth.decode_ad_access_token(access_token)
#                     else:
#                         response = unauthorized_message()
#                         return add_security_headers(response)
#                 access_token_expiry_time = decoded_token.get('exp')
#                 if access_token_expiry_time > time.time():
#                     # access_token is valid
#                     response = await self.get_response(request, call_next)
#                     return add_security_headers(response)
#             elif settings.authentication_ad_enabled:
#                 decoded_token = auth.decode_ad_access_token(access_token)
#                 access_token_expiry_time = decoded_token.get('exp')
#                 if access_token_expiry_time > time.time():
#                     # access_token is valid
#                     response = await self.get_response(request, call_next)
#                     return add_security_headers(response)
#             else:
#                 log.error('Unable to verify access token as no auth mode is enabled')
#                 response = await self.get_response(request, call_next)
#                 return add_security_headers(response)
#
#         except Exception as exception:
#             log.error(exception)
#             log.error(traceback.format_exc())
#         response = unauthorized_message()
#         return add_security_headers(response)
