"""Модуль регистрации глобальных обработчиков кастомных исключений."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    FaceitEntityNotFound,
    ExternalServiceUnavailable,
    InsufficientDataError,
)


async def faceit_entity_not_found_handler(
    request: Request,
    exc: FaceitEntityNotFound,
):
    """Обработка ошибок отсутствия данных в Faceit API (404)."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.message},
    )


async def external_service_unavailable_handler(
    request: Request,
    exc: ExternalServiceUnavailable,
):
    """Обработка ошибок недоступности внешних сервисов (503)."""
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": exc.message},
    )


async def insufficient_data_handler(
    request: Request,
    exc: InsufficientDataError,
):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": exc.message},
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Регистрирует все обработчики кастомных исключений в приложении."""
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
