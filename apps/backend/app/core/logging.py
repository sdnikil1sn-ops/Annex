"""Structured logging configuration using structlog.

- JSON output when LOG_JSON=true (production, machine-parsed).
- Pretty console output in development.
- Standard library loggers (including uvicorn) are routed through the same
  formatter so every log line is consistent and queryable.
"""

import logging
from typing import Any

import structlog

from app.core.config import Settings


def _shared_processors() -> list[Any]:
    """Return processors shared by app logs and foreign (stdlib) logs."""
    return [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]


def _renderer(json_mode: bool) -> Any:
    """Return the terminal renderer for the configured output mode."""
    if json_mode:
        return structlog.processors.JSONRenderer()
    return structlog.dev.ConsoleRenderer()


def configure_logging(settings: Settings) -> None:
    """Configure structlog and the standard logging tree for the process."""
    level: int = getattr(logging, settings.log_level.upper())

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=_renderer(settings.log_json),
        foreign_pre_chain=_shared_processors(),
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    # Route uvicorn's loggers through the root handler for consistent output.
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uvicorn_logger = logging.getLogger(name)
        uvicorn_logger.handlers.clear()
        uvicorn_logger.propagate = True

    processors: list[Any] = [
        *_shared_processors(),
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ]

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
