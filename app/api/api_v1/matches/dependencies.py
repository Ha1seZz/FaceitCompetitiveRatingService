from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.faceit.client import FaceitClient
from app.services.faceit.dependencies import get_faceit_client
from app.core.exceptions import FaceitEntityNotFound, ExternalServiceUnavailable
from app.core.settings import db_helper

from .repository import MatchRepository
from .services.match_service import MatchService


async def get_match_repository(
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> MatchRepository:
    """Dependency для создания MatchRepository."""
    return MatchRepository(session=session)


async def get_match_service(
    session: AsyncSession = Depends(db_helper.session_dependency),
    repository: MatchRepository = Depends(get_match_repository),
) -> MatchService:
    """Dependency для создания MatchService."""
    return MatchService(session=session, repository=repository)


async def get_current_match_details(
    match_id: str,
    faceit_client: FaceitClient = Depends(get_faceit_client),
) -> dict:
    """Получает данные матча из Faceit API."""
    try:
        match_data = await faceit_client.get_match(match_id=match_id)
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

    # Проверка статуса матча
    if match_data["status"] != "FINISHED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Match must be finished",
        )

    return match_data
