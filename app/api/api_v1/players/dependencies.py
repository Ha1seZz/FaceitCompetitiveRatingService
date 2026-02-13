"""Зависимости модуля игроков."""

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.application import (
    MapsStatsService,
    PlayerService,
    PlayerAnalysisService,
    TimeAnalysisService,
    MatchHistoryService,
)
from app.infrastructure.db.repositories import (
    MapsStatsRepository,
    MatchHistoryRepository,
    PlayerRepository,
)
from app.infrastructure.faceit.dependencies import get_faceit_client
from app.infrastructure.faceit.client import FaceitClient
from app.core.settings import db_helper


async def get_player_repository(
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> PlayerRepository:
    """Создает экземпляр репозитория игроков."""
    return PlayerRepository(session=session)


async def get_player_service(
    repository: PlayerRepository = Depends(get_player_repository),
    faceit_client: FaceitClient = Depends(get_faceit_client),
) -> PlayerService:
    """Создает экземпляр сервиса обработки логики игроков."""
    return PlayerService(
        repository=repository,
        faceit_client=faceit_client,
    )


async def get_maps_stats_repository(
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> MapsStatsRepository:
    """Создает экземпляр репозитория статистики по картам."""
    return MapsStatsRepository(session=session)


async def get_maps_stats_service(
    repository: MapsStatsRepository = Depends(get_maps_stats_repository),
    faceit_client: FaceitClient = Depends(get_faceit_client),
) -> MapsStatsService:
    """Создает экземпляр сервиса статистики по картам."""
    return MapsStatsService(
        repository=repository,
        faceit_client=faceit_client,
    )


async def get_player_analysis_service(
    maps_service: MapsStatsService = Depends(get_maps_stats_service),
    player_service: PlayerService = Depends(get_player_service),
) -> PlayerAnalysisService:
    """Dependency-фабрика для PlayerAnalysisService."""
    return PlayerAnalysisService(
        maps_service=maps_service,
        player_service=player_service,
    )


def get_match_history_repository(
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> MatchHistoryRepository:
    """Dependency-фабрика для репозитория кэша истории матчей игрока."""
    return MatchHistoryRepository(session=session)


def get_match_history_service(
    match_history_repo: MatchHistoryRepository = Depends(get_match_history_repository),
    player_repo: PlayerRepository = Depends(get_player_repository),
    faceit_client: FaceitClient = Depends(get_faceit_client),
) -> MatchHistoryService:
    """Dependency-фабрика для сервиса кэширования истории матчей игрока."""
    return MatchHistoryService(
        match_history_repo=match_history_repo,
        player_repo=player_repo,
        faceit_client=faceit_client,
    )


def get_time_analysis_service(
    player_service: PlayerService = Depends(get_player_service),
    match_history_service: MatchHistoryService = Depends(get_match_history_service),
) -> TimeAnalysisService:
    """Dependency-фабрика для TimeAnalysisService."""
    return TimeAnalysisService(
        player_service=player_service,
        match_history_service=match_history_service,
    )


async def get_current_faceit_player(
    nickname: str,
    faceit_client: FaceitClient = Depends(get_faceit_client),
) -> dict:
    """Запрашивает данные игрока напрямую из Faceit API."""
    return await faceit_client.get_player(nickname=nickname)
