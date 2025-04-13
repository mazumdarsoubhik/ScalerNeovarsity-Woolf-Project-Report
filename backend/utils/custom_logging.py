import sys
import os
import logging
from logging import Logger
from logging.handlers import TimedRotatingFileHandler
from core.config import settings
from middleware.context import current_username, current_ip


class LogFilter(logging.Filter):
    """
        Log filter to get module path
    """

    def filter(self, record: logging.LogRecord) -> bool:
        file_path = record.pathname
        record.pathname = os.path.relpath(file_path, settings.project_root_path)
        record.username = current_username.get()
        record.ipaddress = current_ip.get()
        return True


def get_logger() -> Logger:
    """
        Returns logger to log into azure terminal
    """
    logger = logging.getLogger(settings.project_name)

    logger.setLevel(settings.logging_level)

    logging_format = '%(asctime)s [%(ipaddress)s] [%(processName)s] [%(threadName)s] %(levelname)s %(pathname)s:%(lineno)d [%(username)s] - %(message)s'
    formatter = logging.Formatter(logging_format)
    logger.propagate = False
    logger_handlers = logger.handlers

    if len(logger_handlers) == 0:
        # Stream handler (console)
        handler = logging.StreamHandler(sys.stdout)

        handler.addFilter(LogFilter())
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        if settings.logging_file_logging_enabled:
            # File handler with daily rotation
            log_file_path = os.path.join(settings.logging_folder_path, "app.log")
            # Ensure the logs directory exists
            os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

            file_handler = TimedRotatingFileHandler(
                log_file_path, when="midnight", interval=1, backupCount=settings.logging_backup_count
            )
            file_handler.addFilter(LogFilter())
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    logger.info("Logger %s initialized with level %s", settings.project_name_short, logging.getLevelName(settings.logging_level))
    return logger


log = get_logger()