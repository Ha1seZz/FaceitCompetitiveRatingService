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
    """Получает данные о матче из Faceit и синхронизирует матч в БД."""
    match = await match_service.create_or_update_from_faceit(match_data)
    return match
