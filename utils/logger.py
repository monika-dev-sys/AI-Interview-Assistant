"""
utils/logger.py
Centralised Loguru logger with console + rotating file sink.
"""
import sys
from loguru import logger
from config.settings import settings

logger.remove()  # Remove default handler

logger.add(
    sys.stderr,
    level=settings.LOG_LEVEL,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - {message}",
    colorize=True,
)

logger.add(
    settings.BASE_DIR / "logs" / "app.log",
    level="DEBUG",
    rotation="10 MB",
    retention="7 days",
    compression="zip",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{line} - {message}",
    enqueue=True,
)

__all__ = ["logger"]
