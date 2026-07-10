"""HTTP-эндпоинты игроков: список/профиль/карты/анализ/удаление."""

from fastapi import APIRouter, Depends, Query, Request, status
from fastapi_cache.decorator import cache

from app.application import (
    MapsStatsService,
    PlayerService,
    PlayerStatsService,
    TimeAnalysisService,
)
from app.core.config import settings
from app.core.limiter import limiter
from app.schemas import (
    MapsInsight,
    MapStatsResponse,
    PlayerProfileDetails,
    PlayerCSRating,
    PlayerPublic,
    PlayerStatsInsight,
    WhenToPlayInsight,
)
from .dependencies import (
    get_maps_stats_service,
    get_player_service,
    get_player_stats_service,
    get_time_analysis_service,
)

router = APIRouter(
    prefix=settings.api.v1.players,  # /players
    tags=["Players"],
)


@router.get("/", response_model=list[PlayerPublic])
@limiter.limit(settings.rate_limit.default)
@cache(expire=30)
async def get_players(
    request: Request,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    player_service: PlayerService = Depends(get_player_service),
):
    """Получить всех игроков из локальной базы данных."""
    return await player_service.get_players(limit=limit, offset=offset)


@router.get("/{nickname}", response_model=PlayerProfileDetails)
@limiter.limit(settings.rate_limit.expensive)
@cache(expire=60)
async def get_player_profile(
    request: Request,
    nickname: str,
    player_service: PlayerService = Depends(get_player_service),
):
    """Получить базовый профиль игрока."""
    return await player_service.get_or_fetch_player(nickname=nickname)


@router.get("/{nickname}/rating", response_model=PlayerCSRating)
@limiter.limit(settings.rate_limit.expensive)
@cache(expire=60)
async def get_player_rating(
    request: Request,
    nickname: str,
    player_service: PlayerService = Depends(get_player_service),
):
    """Получить текущее ELO и уровень игрока."""
    return await player_service.get_or_fetch_player(nickname=nickname)


@router.get("/{nickname}/stats", response_model=PlayerStatsInsight)
@limiter.limit(settings.rate_limit.expensive)
@cache(expire=120)
async def get_player_stats(
    request: Request,
    nickname: str,
    player_service: PlayerService = Depends(get_player_service),
    player_stats_service: PlayerStatsService = Depends(get_player_stats_service),
):
    """Получить агрегированную статистику игрока за последние 30 матчей."""
    player = await player_service.get_or_fetch_player(nickname=nickname)
    return await player_stats_service.get_or_fetch_player_stats(player.player_id)


@router.get("/{nickname}/maps", response_model=list[MapStatsResponse])
@limiter.limit(settings.rate_limit.expensive)
@cache(expire=300)
async def get_player_maps_stats(
    request: Request,
    nickname: str,
    player_service: PlayerService = Depends(get_player_service),
    maps_service: MapsStatsService = Depends(get_maps_stats_service),
):
    """Получить сырую статистику по картам."""
    player = await player_service.get_or_fetch_player(nickname=nickname)
    return await maps_service.get_or_fetch_maps_stats(player.player_id)


@router.get("/{nickname}/insights/maps", response_model=MapsInsight)
@limiter.limit(settings.rate_limit.expensive)
@cache(expire=300)
async def get_maps_insight(
    request: Request,
    nickname: str,
    player_service: PlayerService = Depends(get_player_service),
    maps_service: MapsStatsService = Depends(get_maps_stats_service),
):
    """Аналитика: лучшие и худшие карты."""
    player = await player_service.get_or_fetch_player(nickname=nickname)
    return await maps_service.analyze(player.player_id)


@router.get("/{nickname}/insights/schedule", response_model=WhenToPlayInsight)
@limiter.limit(settings.rate_limit.expensive)
async def get_schedule_insight(
    request: Request,
    nickname: str,
    time_analysis_service: TimeAnalysisService = Depends(get_time_analysis_service),
):
    """Аналитика: оптимальное время для игры в формате UTC."""
    best_window = await time_analysis_service.analyze(nickname)
    end_hour = (best_window.start_hour + best_window.window_size_hours) % 24

    return WhenToPlayInsight(
        start_hour=best_window.start_hour,
        end_hour=end_hour,
        matches=best_window.matches,
        wins=best_window.wins,
        winrate=float(best_window.winrate_percent),
    )


@router.delete("/{nickname}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(settings.rate_limit.expensive)
async def delete_player(
    request: Request,
    nickname: str,
    player_service: PlayerService = Depends(get_player_service),
):
    """Удалить игрока из локальной базы данных."""
    await player_service.delete_player_by_nickname(nickname=nickname)
