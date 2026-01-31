"""Главный маршрутизатор API."""

from fastapi import APIRouter

from app.core.config import settings
from .api_v1 import router as router_api_v1


# Главный роутер для всего API приложения
router = APIRouter(
    prefix=settings.api.prefix,  # /api
)
router.include_router(router_api_v1)  # /api/v1
