"""Маршрутизатор API v1."""

from fastapi import APIRouter

from app.core.config import settings

from .players.endpoints import router as players_router
from .matches.endpoints import router as matches_router
from .system.endpoints import router as system_router

# Роутер для версии v1
router = APIRouter(prefix=settings.api.v1.prefix)  # /v1
router.include_router(players_router)  # /v1/players
router.include_router(matches_router)  # /v1/matches
router.include_router(system_router)  # /v1/system
