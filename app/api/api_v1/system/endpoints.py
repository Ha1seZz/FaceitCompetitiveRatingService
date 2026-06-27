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
    """
    Liveness-пробег: проверка работоспособности event-loop.
    """
    return {"status": "alive"}


@router.get("/ready")
async def readiness_check(request: Request):
    """Readiness-пробег: проверка готовности сервиса принимать пользовательский трафик."""
    deps_status = {"database": "ok", "httpx_client": "ok"}
    is_ready = True

    try:
        await db_helper.ping()
    except Exception as e:
        logger.error(
            "Readiness check failed: Database is unreachable: {error}",
            error=e,
        )
        deps_status["database"] = "unavailable"
        is_ready = False

    if not hasattr(request.app.state, "httpx_client"):
        logger.error(
            "Readiness check failed: HTTPX client not initialized in app.state"
        )
        deps_status["httpx_client"] = "unavailable"
        is_ready = False

    if not is_ready:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not ready", "dependencies": deps_status},
        )

    return {"status": "ready", "dependencies": deps_status}
