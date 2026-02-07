"""Зависимости модуля матчей."""

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.faceit.client import FaceitClient
from app.infrastructure.faceit.dependencies import get_faceit_client
from app.core.settings import db_helper

from .repository import MatchRepository
from .services.match_service import MatchService


async def get_match_repository(
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> MatchRepository:
    """Создает экземпляр репозитория матчей."""
    return MatchRepository(session=session)


async def get_match_service(
    session: AsyncSession = Depends(db_helper.session_dependency),
    repository: MatchRepository = Depends(get_match_repository),
) -> MatchService:
    """Создает экземпляр сервиса обработки логики матчей."""
    return MatchService(session=session, repository=repository)


async def get_current_match_details(
    match_id: str,
    faceit_client: FaceitClient = Depends(get_faceit_client),
) -> dict:
    """Получает матч из Faceit и гарантирует, что он завершен (FINISHED)."""
    match_data = await faceit_client.get_match(match_id=match_id)

    # Валидация жизненного цикла матча
    if match_data["status"] != "FINISHED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Match must be finished",
        )

    return match_data
