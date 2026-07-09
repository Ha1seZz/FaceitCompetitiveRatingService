"""Зависимости модуля игроков."""

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import BackgroundTasks, Depends
from redis.asyncio import Redis

from app.application import (
    MapsStatsService,
    MatchHistoryService,
    PlayerService,
    PlayerStatsService,
    TimeAnalysisService,
)
from app.infrastructure.db.repositories import (
    MapsStatsRepository,
    MatchHistoryRepository,
    PlayerRepository,
    PlayerStatsRepository,
)
from app.infrastructure.faceit.dependencies import get_faceit_client
from app.infrastructure.faceit.client import FaceitClient
from app.core.settings import db_helper
from app.core.redis import get_redis_client


async def get_player_repository(
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> PlayerRepository:
    """Создает экземпляр репозитория игроков."""
    return PlayerRepository(session=session)


async def get_player_stats_repository(
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> PlayerStatsRepository:
    """Создает экземпляр репозитория игроков."""
    return PlayerStatsRepository(session=session)


async def get_player_service(
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(db_helper.session_dependency),
    player_repo: PlayerRepository = Depends(get_player_repository),
    faceit_client: FaceitClient = Depends(get_faceit_client),
) -> PlayerService:
    """Создает экземпляр сервиса обработки логики игроков."""
    redis_client: Redis = get_redis_client()

    return PlayerService(
        session=session,
        player_repo=player_repo,
        faceit_client=faceit_client,
        bg_tasks=background_tasks,
        redis=redis_client,
    )


async def get_player_stats_service(
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(db_helper.session_dependency),
    stats_repo: PlayerStatsRepository = Depends(get_player_stats_repository),
    faceit_client: FaceitClient = Depends(get_faceit_client),
) -> PlayerStatsService:
    """Создает экземпляр сервиса обработки статистики игроков."""
    return PlayerStatsService(
        session=session,
        stats_repo=stats_repo,
        faceit_client=faceit_client,
        bg_tasks=background_tasks,
    )


async def get_maps_stats_repository(
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> MapsStatsRepository:
    """Создает экземпляр репозитория статистики по картам."""
    return MapsStatsRepository(session=session)


async def get_maps_stats_service(
    session: AsyncSession = Depends(db_helper.session_dependency),
    maps_stats_repo: MapsStatsRepository = Depends(get_maps_stats_repository),
    faceit_client: FaceitClient = Depends(get_faceit_client),
) -> MapsStatsService:
    """Создает экземпляр сервиса статистики по картам."""
    return MapsStatsService(
        session=session,
        maps_stats_repo=maps_stats_repo,
        faceit_client=faceit_client,
    )


async def get_match_history_repository(
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> MatchHistoryRepository:
    """Dependency-фабрика для репозитория кэша истории матчей игрока."""
    return MatchHistoryRepository(session=session)


async def get_match_history_service(
    background_tasks: BackgroundTasks,
    match_history_repo: MatchHistoryRepository = Depends(get_match_history_repository),
    player_repo: PlayerRepository = Depends(get_player_repository),
    faceit_client: FaceitClient = Depends(get_faceit_client),
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> MatchHistoryService:
    """Dependency-фабрика для сервиса кэширования истории матчей игрока."""
    redis_client: Redis = get_redis_client()

    return MatchHistoryService(
        match_history_repo=match_history_repo,
        player_repo=player_repo,
        faceit_client=faceit_client,
        session=session,
        bg_tasks=background_tasks,
        redis=redis_client,
    )


async def get_time_analysis_service(
    player_service: PlayerService = Depends(get_player_service),
    match_history_service: MatchHistoryService = Depends(get_match_history_service),
) -> TimeAnalysisService:
    """Dependency-фабрика для TimeAnalysisService."""
    return TimeAnalysisService(
        player_service=player_service,
        match_history_service=match_history_service,
    )
