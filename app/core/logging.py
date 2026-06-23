"""Logging configuration for DataContractor.

Supports both plain-text (development) and JSON-structured (production)
log output.  The log level and format are driven by the application
settings.
"""

import json
import logging
import sys
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    """Output log records as newline-delimited JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        return json.dumps(
            {
                "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "line": record.lineno,
            },
            default=str,
        )


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configure the root logger and return a ``datacontractor`` logger instance.

    Args:
        level: One of ``DEBUG``, ``INFO``, ``WARNING``, ``ERROR``.
               Invalid values silently fall back to ``INFO``.

    Returns:
        The ``datacontractor`` logger.
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    # JSON format is used when the APP_LOG_FORMAT setting is "json".
    # For most cases the format is set once at import time, but we
    # defer the import of ``settings`` to avoid circular imports.
    fmt = "json"
    try:
        from app.core.config import settings as _cfg

        fmt = _cfg.APP_LOG_FORMAT
    except Exception:  # noqa: BLE001
        pass

    if fmt == "json":
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

    root = logging.getLogger()
    root.setLevel(log_level)
    # Avoid duplicate handlers on repeated setup_logging calls
    root.handlers.clear()
    root.addHandler(handler)

    logger = logging.getLogger("datacontractor")
    return logger
