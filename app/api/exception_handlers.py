"""Модуль регистрации глобальных обработчиков кастомных исключений."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.exceptions import (
    FaceitEntityNotFound,
    ExternalServiceUnavailable,
    InsufficientDataError,
    PlayerNotFoundError,
    QueueServiceUnavailableError,
    ResourceLockedError,
)


async def faceit_entity_not_found_handler(
    request: Request,
    exc: FaceitEntityNotFound,
):
    """Обработка ошибок отсутствия данных в Faceit API (404)."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


async def player_not_found_handler(
    request: Request,
    exc: PlayerNotFoundError,
):
    """Обработка ситуации, когда игрок не найден в базе данных."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


async def insufficient_data_handler(
    request: Request,
    exc: InsufficientDataError,
):
    """Обработка ситуации, когда данных недостаточно для аналитики (422)."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": str(exc)},
    )


async def external_service_unavailable_handler(
    request: Request,
    exc: ExternalServiceUnavailable,
):
    """Обработка ошибок недоступности внешних сервисов (503)."""
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": str(exc)},
    )


async def queue_unavailable_exception_handler(
    request: Request,
    exc: QueueServiceUnavailableError,
):
    """Обработка ошибок недоступности сервиса фоновых задач (503)."""
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": str(exc)},
    )


async def resource_locked_exception_handler(
    request: Request,
    exc: ResourceLockedError,
):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc)},
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Регистрирует все обработчики кастомных исключений в приложении."""
    app.add_exception_handler(
        RateLimitExceeded,
        _rate_limit_exceeded_handler,
    )
    app.add_exception_handler(
        FaceitEntityNotFound,
        faceit_entity_not_found_handler,
    )
    app.add_exception_handler(
        ExternalServiceUnavailable,
        external_service_unavailable_handler,
    )
    app.add_exception_handler(
        InsufficientDataError,
        insufficient_data_handler,
    )
    app.add_exception_handler(
        PlayerNotFoundError,
        player_not_found_handler,
    )
    app.add_exception_handler(
        QueueServiceUnavailableError,
        queue_unavailable_exception_handler,
    )
    app.add_exception_handler(
        ResourceLockedError,
        resource_locked_exception_handler,
    )
