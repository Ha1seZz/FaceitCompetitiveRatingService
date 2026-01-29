from fastapi import APIRouter, Depends, HTTPException, status

from .dependencies import get_current_faceit_player

from .services.faceit_client import FaceitClient
from .schemas import PlayerProfileDetails, PlayerCSStats
from core.config import settings


router = APIRouter(
    prefix=settings.api.v1.players,  # /players
    tags=["Players"],
)


@router.get("/profile/{nickname}", response_model=PlayerProfileDetails)
async def get_player_profile(player: dict = Depends(get_current_faceit_player)):
    """Получает информацию об профиле игрока на Faceit."""
    return player


@router.get("/CSStats/{nickname}", response_model=PlayerCSStats)
async def get_cs_stats(player: dict = Depends(get_current_faceit_player)):
    """Получает CS статистику игрока на Faceit."""
    return player
