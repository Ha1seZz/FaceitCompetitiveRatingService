"""Инициализация API версии 1."""

from fastapi import (
    APIRouter,
    Depends,
)
from fastapi.security import HTTPBearer

from app.core.config import settings

from .players.endpoints import router as players_router
from .matches.endpoints import router as matches_router


http_bearer = HTTPBearer(auto_error=False)

# Роутер для версии v1
router = APIRouter(
    prefix=settings.api.v1.prefix,  # /v1
    dependencies=[Depends(http_bearer)],
)
router.include_router(players_router)  # /v1/players
router.include_router(matches_router)  # /v1/matches
