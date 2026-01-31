from fastapi import APIRouter, Depends

from .services.player_service import PlayerService
from .dependencies import get_current_faceit_player, get_player_service
from .schemas import PlayerProfileDetails, PlayerCSStats
from app.core.config import settings


router = APIRouter(
    prefix=settings.api.v1.players,  # /players
    tags=["Players"],
)


@router.get("/profile/{nickname}", response_model=PlayerProfileDetails)
async def get_player_profile(
    player_data: dict = Depends(get_current_faceit_player),
    player_service: PlayerService = Depends(get_player_service),
):
    """Получает данные об игроке из Faceit и синхронизирует игрока в БД."""
    player = await player_service.create_or_update_from_faceit(player_data)
    return player


@router.get("/cs-stats/{nickname}", response_model=PlayerCSStats)
async def get_player_cs_stats(player: dict = Depends(get_current_faceit_player)):
    """Получает Counter-Strike статистику игрока на Faceit."""
    return player
