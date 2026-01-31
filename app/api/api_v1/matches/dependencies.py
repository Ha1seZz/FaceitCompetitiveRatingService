from fastapi import Depends, HTTPException, status

from app.services.faceit.dependencies import get_faceit_client
from app.services.faceit.client import FaceitClient
from app.core.exceptions import FaceitEntityNotFound, ExternalServiceUnavailable


async def get_current_match_details(match_id: str, faceit_client: FaceitClient = Depends(get_faceit_client),) -> dict:
    """Получает данные матча из Faceit API."""
    try:
        match_data = await faceit_client.get_match(match_id=match_id)
    except FaceitEntityNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ExternalServiceUnavailable as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )
    
    # Проверка статуса матча
    if match_data["status"] != "FINISHED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Match must be finished",
        )
    
    return match_data
