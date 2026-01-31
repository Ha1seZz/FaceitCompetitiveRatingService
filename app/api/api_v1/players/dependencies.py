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
    """Dependency для создания PlayerRepository."""
    return PlayerRepository(session=session)


async def get_player_service(
    session: AsyncSession = Depends(db_helper.session_dependency),
    repository: PlayerRepository = Depends(get_player_repository),
) -> PlayerService:
    """Dependency для создания PlayerService."""
    return PlayerService(session=session, repository=repository)


async def get_current_faceit_player(
    nickname: str,
    faceit_client: FaceitClient = Depends(get_faceit_client),
) -> dict:
    """Получает данные игрока из Faceit API."""
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
