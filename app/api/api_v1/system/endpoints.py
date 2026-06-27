"""Системные эндпоинты для мониторинга состояния сервиса."""

import httpx
from loguru import logger
from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException, Request, status

from app.core.settings.db_helper import db_helper
from app.core.config import settings

router = APIRouter(
    prefix=settings.api.v1.system,  # /system
    tags=["System"],
)


@router.get("/health")
async def health_check():
    """Liveness-проверка: жив ли процесс и доступна ли БД."""
    try:
        await db_helper.ping()
    except Exception as e:
        logger.error(
            "Health check failed: Database is unreachable: {error}",
            error=e,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        )

    return {"status": "healthy"}


@router.get("/ready")
async def readiness_check(request: Request):
    """Readiness-проверка: готов ли сервис принимать трафик."""
    status = {"database": "ok", "faceit_api": "ok"}
    is_ready = True

    try:
        await db_helper.ping()
    except Exception as e:
        logger.error(
            "Readiness check: database unavailable: {error}",
            error=e,
        )
        status["database"] = "unavailable"
        is_ready = False

    try:
        httpx_client: httpx.AsyncClient = request.app.state.httpx_client
        response = await httpx_client.get("/games", params={"limit": 1})
        response.raise_for_status()
    except Exception as e:
        logger.error(
            "Readiness check: Faceit API unavailable: {error}",
            error=e,
        )
        status["faceit_api"] = "unavailable"
        is_ready = False

    if not is_ready:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not ready", "dependencies": status},
        )

    return {"status": "ready", "dependencies": status}
