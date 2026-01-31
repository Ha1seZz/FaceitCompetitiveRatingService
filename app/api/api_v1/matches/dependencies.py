from fastapi import HTTPException, status
from app.services.faceit.client import FaceitClient


async def get_current_match_details(match_id: str) -> dict:
    match_data = await FaceitClient().get_match_details(match_id=match_id)
    if not match_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Match not found on Faceit",
        )
    elif match_data["status"] != "FINISHED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Match must be finished",
        )
    return match_data
