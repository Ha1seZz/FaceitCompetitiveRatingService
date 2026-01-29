from fastapi import (
    APIRouter,
    Depends,
)
from fastapi.security import HTTPBearer

from core.config import settings

from .players.endpoints import router as players_router


http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(  # Роутер для версии v1
    prefix=settings.api.v1.prefix,  # /v1
    # Зависимость авторизации для всех эндпоинтов внутри v1
    dependencies=[Depends(http_bearer)],
)
router.include_router(players_router)
