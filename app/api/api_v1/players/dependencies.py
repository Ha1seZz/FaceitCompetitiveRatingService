from fastapi import Depends, HTTPException, status

from app.services.faceit.dependencies import get_faceit_client
from app.services.faceit.client import FaceitClient
from app.core.exceptions import FaceitEntityNotFound, ExternalServiceUnavailable


async def get_current_faceit_player(
    nickname: str,
    faceit_client: FaceitClient = Depends(get_faceit_client),
) -> dict:
    """Получает данные игрока из Faceit API."""
    try:
        return await faceit_client.get_player(nickname=nickname)
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
