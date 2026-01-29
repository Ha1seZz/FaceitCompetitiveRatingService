from fastapi import APIRouter

from app.core.config import settings
from .api_v1 import router as router_api_v1


router = APIRouter(  # Создаем главный роутер для всего API
    prefix=settings.api.prefix,  # /api
)
router.include_router(router_api_v1)  # /api/v1
