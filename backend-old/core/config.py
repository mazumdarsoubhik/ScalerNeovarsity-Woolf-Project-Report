import logging
import os
from datetime import datetime
from typing import Union
from pytz import timezone
from dotenv import load_dotenv


class Settings:
    """
        Project Settings
        Versioning Rules (v1.2.3):
        1. Major version: Incremented when there are incompatible changes
        2. Minor version: Incremented when new features are added in a backward-compatible manner
        3. Patch version: Incremented when backward-compatible bug fixes are made
    """
    project_version = 'v1.0.0'
    project_name = 'Agentic AI Chatbot'
    project_name_short = 'AGENTIC_AI_CHATBOT'  # Make sure no space in the short name
    project_root_path = None
    environment = 'local'  # Valid options are 'local', 'staging' and 'production'
    gcp_project_id = None
    server_start_time = None
    allowed_origins = []
    allowed_credentials = False
    authentication_modes = []  # Valid options are 'basic', 'ad' and 'all'
    authentication_basic_enabled = False
    authentication_ad_enabled = False
    basic_authentication_max_invalid_login_attempts = 3  # Only required if basic authentication is enabled
    access_token_expiry = 60 * 24  # 24 hours (in minutes) only applicable for basic authentication
    refresh_token_expiry = 60 * 24 * 7  # 7 days (in minutes) only applicable for basic authentication
    jwt_algorithm = "HS512"  # only applicable for basic authentication
    db_connection_pool_size = 5
    db_connection_max_overflow = 50
    redis_pool_size = 5
    redis_cache_ttl_xxs = 10  # 10 seconds
    redis_cache_ttl_xs = 60  # 1 min
    redis_cache_ttl_s = 300  # 5 min
    redis_cache_ttl_m = 1800  # 30 Min
    redis_cache_ttl_l = 3600  # 1 Hrs
    redis_cache_ttl_xl = 43200  # 12 Hrs
    redis_cache_ttl_xxl = 86400  # 24 Hrs
    redis_cache_analytics_ttl = 14400  # 4 Hrs
    redis_pubsub_timeout_duration = 180  # 2 min
    logging_level = logging.INFO
    logging_file_logging_enabled = False
    logging_folder_path = ""
    logging_backup_count = 30  # No of days of backup to be kept


settings = Settings()
