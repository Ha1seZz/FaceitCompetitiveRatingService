"""Настройка логирования приложения."""

import sys
import logging
from loguru import logger


class InterceptHandler(logging.Handler):
    """
    Перехватчик стандартных логов Python.
    Берет логи от Uvicorn/SQLAlchemy и пересылает их в Loguru.
    """

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging():
    """Инициализация глобальных настроек Loguru."""

    logger.remove()

    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<magenta>[{extra[request_id]}]</magenta> - "
        "<level>{message}</level>"
    )
    logger.add(
        sys.stdout,
        level="DEBUG",
        format=console_format,
        colorize=True,
        enqueue=True,
    )
    logger.configure(extra={"request_id": "system"})

    logging.root.handlers = []
    logging.root.setLevel(logging.INFO)

    intercept_handler = InterceptHandler()

    target_loggers = ["uvicorn", "uvicorn.error", "sqlalchemy.engine"]

    for logger_name in target_loggers:
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [intercept_handler]
        logging_logger.propagate = False

    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
