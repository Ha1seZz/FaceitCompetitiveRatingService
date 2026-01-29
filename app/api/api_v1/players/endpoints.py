from fastapi import APIRouter, HTTPException, status

from .services.faceit_client import FaceitClient
from .schemas import PlayerDetails
from core.config import settings


router = APIRouter(
    prefix=settings.api.v1.players,  # /players
    tags=["Players"],
)


@router.get("/{nickname}", response_model=PlayerDetails)
async def get_player_profile(nickname: str):
    """Получает информацию об игроке из Faceit."""
    player_details = await FaceitClient().get_player_details(nickname=nickname)

    if not player_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found on Faceit",
        )

    return player_details
