import logging
from typing import Final

from app.core.config import settings

LOG_FORMAT: Final[str] = "%(asctime)s | %(levelname)s | BOOT_ID=%(boot_id)s | %(name)s | %(message)s"
DATE_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"
DEFAULT_LEVEL: Final[str] = "INFO"


class BootIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        """Attach the process BOOT_ID to every emitted log record."""
        record.boot_id = settings.boot_id
        return True


def _parse_level(level: int | str) -> int:
    """Convert a log level name or int into a valid logging level."""
    if isinstance(level, int):
        return level
    parsed = logging.getLevelName(level.upper())
    return parsed if isinstance(parsed, int) else logging.INFO


def configure_logging(level: int | str = DEFAULT_LEVEL) -> None:
    """Configure root logging once with BOOT_ID-aware formatting."""
    root_logger = logging.getLogger()

    if getattr(root_logger, "_nutriflow_custom_logging", False):
        root_logger.setLevel(_parse_level(level))
        return

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    handler.addFilter(BootIdFilter())

    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(_parse_level(level))
    root_logger._nutriflow_custom_logging = True


def get_logger(name: str) -> logging.Logger:
    """Return a module-specific logger instance."""
    return logging.getLogger(name)
