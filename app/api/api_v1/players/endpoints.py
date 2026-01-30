from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .crud import create_or_update_player
from app.core.settings.db_helper import db_helper
from .dependencies import get_current_faceit_player
from .schemas import PlayerProfileDetails, PlayerCSStats
from app.core.config import settings


router = APIRouter(
    prefix=settings.api.v1.players,  # /players
    tags=["Players"],
)


@router.get("/profile/{nickname}", response_model=PlayerProfileDetails)
async def get_player_profile(
    player: dict = Depends(get_current_faceit_player),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    """Получает данные об игроке из Faceit и синхронизирует игрока в БД."""
    await create_or_update_player(session=session, player_in=player)
    return player


@router.get("/cs-stats/{nickname}", response_model=PlayerCSStats)
async def get_player_cs_stats(player: dict = Depends(get_current_faceit_player)):
    """Получает Counter-Strike статистику игрока на Faceit."""
    return player
