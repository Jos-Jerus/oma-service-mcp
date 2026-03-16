"""Logging utilities for OMA Service MCP Server."""

import logging
import re
import sys


class SensitiveFormatter(logging.Formatter):
    """Formatter that removes sensitive info from log messages."""

    DEFAULT_FORMAT = (
        "%(asctime)s - %(name)s - %(levelname)-8s - %(thread)d:%(process)d "
        "- %(message)s - (%(pathname)s:%(lineno)d)->%(funcName)s"
    )

    def __init__(self, fmt: str | None = None) -> None:
        """Initialize with default format if none provided."""
        if fmt is None:
            fmt = self.DEFAULT_FORMAT
        super().__init__(fmt)

    @staticmethod
    def _filter(s: str) -> str:
        s = re.sub(r"(token['\"]?\s*[:=]\s*)['\"]?[^'\",\s}]+", r"\1*** REDACTED ***", s, flags=re.IGNORECASE)
        s = re.sub(r"(Bearer\s+)\S+", r"\1*** REDACTED ***", s)
        return s

    def format(self, record: logging.LogRecord) -> str:
        """Format log record while filtering sensitive information."""
        original = logging.Formatter.format(self, record)
        return self._filter(original)


def get_logging_level() -> int:
    """Get the logging level from settings."""
    from oma_service_mcp.src.settings import settings

    level = settings.LOGGING_LEVEL
    return getattr(logging, str(level).upper(), logging.INFO) if level else logging.INFO


logging.getLogger("requests").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("asyncio").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("httpcore").setLevel(logging.ERROR)


def add_log_file_handler(logger: logging.Logger, filename: str) -> logging.FileHandler:
    """Add a file handler to the logger with sensitive information filtering."""
    fh = logging.FileHandler(filename)
    fh.setFormatter(SensitiveFormatter())
    logger.addHandler(fh)
    return fh


def add_stream_handler(logger: logging.Logger) -> None:
    """Add a stream handler to the logger with sensitive information filtering."""
    ch = logging.StreamHandler(sys.stderr)
    ch.setFormatter(SensitiveFormatter())
    logger.addHandler(ch)


# Module-level logger with safe default name
log = logging.getLogger("oma-service-mcp")


def configure_logging() -> logging.Logger:
    """Configure logging after settings are available.

    Returns:
        logging.Logger: The configured application logger.
    """
    from oma_service_mcp.src.settings import settings

    logger_name = settings.LOGGER_NAME or "oma-service-mcp"
    target_logger = logging.getLogger(logger_name)

    # Configure third-party loggers
    logging.getLogger("requests").setLevel(logging.ERROR)
    logging.getLogger("httpx").setLevel(logging.ERROR)
    logging.getLogger("httpcore").setLevel(logging.ERROR)
    urllib3_logger = logging.getLogger("urllib3")

    # Reset handlers to prevent duplicates on reconfiguration
    for handler in target_logger.handlers:
        handler.close()
    target_logger.handlers = []
    for handler in urllib3_logger.handlers:
        handler.close()
    urllib3_logger.handlers = []

    # Set levels
    urllib3_logger.setLevel(logging.ERROR)
    target_logger.setLevel(get_logging_level())

    # Optional file logging
    if settings.LOG_TO_FILE:
        add_log_file_handler(target_logger, "oma-service-mcp.log")
        add_log_file_handler(urllib3_logger, "oma-service-mcp.log")

    # Always add stream handlers
    add_stream_handler(target_logger)
    add_stream_handler(urllib3_logger)

    global log  # pylint: disable=global-statement
    log = target_logger
    return target_logger
