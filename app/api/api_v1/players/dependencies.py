from fastapi import HTTPException, status
from .services.faceit_client import FaceitClient


async def get_current_faceit_player(nickname: str) -> dict:
    player_data = await FaceitClient().get_player_details(nickname=nickname)
    if not player_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found on Faceit",
        )
    return player_data
