"""Эндпоинты для управления данными игроков."""

from fastapi import APIRouter, Depends, Query, status

from .services.player_service import PlayerService
from .dependencies import fetch_player_maps_data, get_current_faceit_player, get_player_service
from .schemas import MapStatsResponse, PlayerProfileDetails, PlayerCSStats, PlayerPublic
from app.core.config import settings


router = APIRouter(
    prefix=settings.api.v1.players,  # /players
    tags=["Players"],
)


@router.get("/", response_model=list[PlayerPublic])
async def get_players(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    player_service: PlayerService = Depends(get_player_service),
):
    """Получить всех игроков из локальной базы данных."""
    return await player_service.get_players(limit=limit, offset=offset)


@router.get("/profile/{nickname}", response_model=PlayerProfileDetails)
async def get_player_profile(
    player_data: dict = Depends(get_current_faceit_player),
    player_service: PlayerService = Depends(get_player_service),
):  
    """Получить профиль игрока и синхронизировать его с локальной базой данных."""
    return await player_service.create_or_update_from_faceit(player_data)


@router.get("/cs-stats/{nickname}", response_model=PlayerCSStats)
async def get_player_cs_stats(player: dict = Depends(get_current_faceit_player)):
    """Получить только Counter-Strike статистику игрока."""
    return player


@router.get("/maps-stats/{nickname}", response_model=list[MapStatsResponse])
async def get_player_maps_stats(
    player_maps_data: dict = Depends(fetch_player_maps_data),
    player_service: PlayerService = Depends(get_player_service),
):
    """Получить детализированную статистику игрока по всем картам."""
    return await player_service.transform_maps_stats(player_maps_data)


@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_player(
    player_id: str,
    player_service: PlayerService = Depends(get_player_service),
):
    """Удалить игрока из локальной базы данных."""
    return await player_service.delete_player(player_id=player_id)
