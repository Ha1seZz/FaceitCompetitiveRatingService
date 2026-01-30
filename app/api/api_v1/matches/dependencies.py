from fastapi import HTTPException, status
from .services.faceit_client import FaceitClient


async def get_current_match_details(match_id: str) -> dict:
    match_data = await FaceitClient().get_match_details(match_id=match_id)
    if not match_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found on Faceit",
        )
    elif match_data["status"] != "FINISHED":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match must be finished",
        )
    return match_data
