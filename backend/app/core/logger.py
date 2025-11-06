"""Application-wide logging configuration using Loguru."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from loguru import logger


LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> "
    "| <level>{level: <8}</level> "
    "| <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> "
    "- <level>{message}</level>"
)


def setup_logging(log_level: str = "INFO", log_file: Optional[Path] = None) -> None:
    """Configure loguru logger for the application."""

    logger.remove()
    logger.add(sys.stderr, level=log_level, format=LOG_FORMAT, enqueue=True, colorize=True)

    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            log_file,
            level=log_level,
            format=LOG_FORMAT,
            enqueue=True,
            rotation="00:00",
            retention="7 days",
            compression="zip",
        )


__all__ = ["setup_logging", "logger"]

