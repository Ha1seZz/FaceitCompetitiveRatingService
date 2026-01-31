"""Эндпоинты для управления данными матчей."""

from fastapi import APIRouter, Depends

from .services.match_service import MatchService
from .dependencies import get_current_match_details, get_match_service
from .schemas import MatchDetails
from app.core.config import settings


router = APIRouter(
    prefix=settings.api.v1.matches,  # /matches
    tags=["Matches"],
)


@router.get("/{match_id}", response_model=MatchDetails)
async def get_match_details(
    match_data: dict = Depends(get_current_match_details),
    match_service: MatchService = Depends(get_match_service),
):
    """Получить детали матча и синхронизировать их с локальной базой данных."""
    match = await match_service.create_or_update_from_faceit(match_data)
    return match


@router.get("/region/{region}", response_model=list[MatchDetails])
async def get_matches_by_region(
    region: str,
    match_service: MatchService = Depends(get_match_service),
):
    """Получить список всех завершенных матчей в указанном регионе."""
    matches = await match_service.get_finished_matches_by_region(region)
    return matches
