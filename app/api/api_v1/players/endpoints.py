from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from crud import create_or_update_player
from core.settings.db_helper import db_helper
from .dependencies import get_current_faceit_player
from .services.faceit_client import FaceitClient
from .schemas import PlayerCreate, PlayerProfileDetails, PlayerCSStats
from core.config import settings


router = APIRouter(
    prefix=settings.api.v1.players,  # /players
    tags=["Players"],
)


@router.get("/profile/{nickname}", response_model=PlayerProfileDetails)
async def get_player_profile(
    player: dict = Depends(get_current_faceit_player),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    """Получает данные об игроке из Faceit и сохраняет игрока в БД."""
    await create_or_update_player(session=session, player_in=player)
    return player


@router.get("/CSStats/{nickname}", response_model=PlayerCSStats)
async def get_cs_stats(player: dict = Depends(get_current_faceit_player)):
    """Получает CS статистику игрока на Faceit."""
    return player
