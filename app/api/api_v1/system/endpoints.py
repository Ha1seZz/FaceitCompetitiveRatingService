from fastapi import APIRouter, HTTPException, status
from loguru import logger

from app.core.settings.db_helper import db_helper
from app.core.config import settings

router = APIRouter(
    prefix=settings.api.v1.system,  # /system
    tags=["System"],
)


@router.get("/health")
async def health_check():
    """Служебный эндпоинт для проверки здоровья сервиса и инфраструктуры."""
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
