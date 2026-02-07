"""Эндпоинты для управления данными матчей."""

from fastapi import APIRouter, Depends, Query, status

from .services.match_service import MatchService
from .dependencies import get_current_match_details, get_match_service
from .schemas import MatchDetails, MatchPublic
from app.core.config import settings


router = APIRouter(
    prefix=settings.api.v1.matches,  # /matches
    tags=["Matches"],
)


@router.get("/", response_model=list[MatchPublic])
async def get_matches(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    match_service: MatchService = Depends(get_match_service),
):
    """Получить все матчи из локальной базы данных."""
    return await match_service.get_matches(limit=limit, offset=offset)


@router.get("/id/{match_id}", response_model=MatchDetails)
async def get_match_details(
    match_data: dict = Depends(get_current_match_details),
    match_service: MatchService = Depends(get_match_service),
):
    """Получить детали матча и синхронизировать их с локальной базой данных."""
    return await match_service.create_or_update_from_faceit(match_data)


@router.get("/region/{region}", response_model=list[MatchDetails])
async def get_matches_by_region(
    region: str,
    match_service: MatchService = Depends(get_match_service),
):
    """Получить список всех завершенных матчей в указанном регионе."""
    return await match_service.get_finished_matches_by_region(region)


@router.delete("/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_match(
    match_id: str,
    match_service: MatchService = Depends(get_match_service),
):
    """Удалить матч из локальной базы данных."""
    return await match_service.delete_match(match_id=match_id)
