"""Корневой роутер /api и подключение версий API."""

from fastapi import APIRouter

from app.core.config import settings
from .api_v1 import router as router_api_v1


router = APIRouter(
    prefix=settings.api.prefix,  # /api
)
router.include_router(router_api_v1)  # /api/v1
