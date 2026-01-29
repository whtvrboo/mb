"""Structured logging configuration."""

import logging
import sys
from typing import Any

from pythonjsonlogger import jsonlogger

from mitlist.core.config import settings
from mitlist.core.request_context import get_group_id, get_trace_id, get_user_id


class ContextFilter(logging.Filter):
    """Add trace_id, user_id, group_id to log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.trace_id = get_trace_id() or ""
        record.user_id = get_user_id() or ""
        record.group_id = get_group_id() or ""
        return True


def setup_logging() -> None:
    """Configure structured logging based on environment."""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Remove existing handlers
    root_logger.handlers.clear()

    handler: logging.StreamHandler[Any]
    if settings.is_production:
        # JSON logging for production
        handler = logging.StreamHandler(sys.stdout)
        formatter = jsonlogger.JsonFormatter(
            "%(timestamp)s %(level)s %(name)s %(message)s %(trace_id)s %(user_id)s %(group_id)s"
        )
        handler.setFormatter(formatter)
    else:
        # Console logging for development
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - [trace_id=%(trace_id)s] "
            "[user_id=%(user_id)s] [group_id=%(group_id)s] - %(message)s"
        )
        handler.setFormatter(formatter)

    handler.addFilter(ContextFilter())
    root_logger.addHandler(handler)
