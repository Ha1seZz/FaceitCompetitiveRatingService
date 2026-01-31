from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .repository import create_or_update_match
from .dependencies import get_current_match_details
from .schemas import MatchDetails
from app.core.settings.db_helper import db_helper
from app.core.config import settings


router = APIRouter(
    prefix=settings.api.v1.matches,  # /matches
    tags=["Matches"],
)


@router.get("/matches/{match_id}", response_model=MatchDetails)
async def get_match_details(
    match: dict = Depends(get_current_match_details),
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    """Получает данные о матче из Faceit и синхронизирует матч в БД."""
    await create_or_update_match(session=session, match_in=match)
    return match
