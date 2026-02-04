"""Зависимости модуля игроков."""

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.api.api_v1.players.services.maps_stats_service import MapsStatsService
from app.api.api_v1.players.maps_stats_repository import MapsStatsRepository
from app.api.api_v1.players.services.player_service import PlayerService
from app.api.api_v1.players.player_repository import PlayerRepository
from app.services.faceit.dependencies import get_faceit_client
from app.services.faceit.client import FaceitClient
from app.core.settings import db_helper


async def get_player_repository(
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> PlayerRepository:
    """Создает экземпляр репозитория игроков."""
    return PlayerRepository(session=session)


async def get_player_service(
    session: AsyncSession = Depends(db_helper.session_dependency),
    repository: PlayerRepository = Depends(get_player_repository),
) -> PlayerService:
    """Создает экземпляр сервиса обработки логики игроков."""
    return PlayerService(session=session, repository=repository)


async def get_maps_stats_repository(
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> MapsStatsRepository:
    """Создает экземпляр репозитория статистики по картам."""
    return MapsStatsRepository(session=session)


async def get_maps_stats_service(
    session: AsyncSession = Depends(db_helper.session_dependency),
    repository: MapsStatsRepository = Depends(get_maps_stats_repository),
    faceit_client: FaceitClient = Depends(get_faceit_client),
) -> MapsStatsService:
    """Создает экземпляр сервиса статистики по картам."""
    return MapsStatsService(
        session=session,
        repository=repository,
        faceit_client=faceit_client,
    )


async def get_current_faceit_player(
    nickname: str,
    faceit_client: FaceitClient = Depends(get_faceit_client),
) -> dict:
    """Запрашивает данные игрока напрямую из Faceit API."""
    return await faceit_client.get_player(nickname=nickname)
