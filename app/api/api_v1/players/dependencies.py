"""Зависимости модуля игроков."""

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.faceit.client import FaceitClient
from app.services.faceit.dependencies import get_faceit_client
from app.core.exceptions import FaceitEntityNotFound, ExternalServiceUnavailable
from app.core.settings import db_helper

from .repository import PlayerRepository
from .services.player_service import PlayerService


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


async def get_current_faceit_player(
    nickname: str,
    faceit_client: FaceitClient = Depends(get_faceit_client),
) -> dict:
    """Запрашивает данные игрока напрямую из Faceit API и обрабатывает ошибки."""
    try:
        return await faceit_client.get_player(nickname=nickname)
    except FaceitEntityNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ExternalServiceUnavailable as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )


async def fetch_player_maps_data(
    nickname: str,
    faceit_client: FaceitClient = Depends(get_faceit_client),
) -> dict:
    """Находит ID игрока по никнейму и запрашивает его статистику."""
    try:
        player_id = await faceit_client.get_player_id_by_nickname(nickname=nickname)
        return await faceit_client.get_player_maps_stats_raw(player_id=player_id)
    except FaceitEntityNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ExternalServiceUnavailable as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )
