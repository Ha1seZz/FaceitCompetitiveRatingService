"""Зависимости для обеспечения доступа к Faceit API."""

from fastapi import Depends
import httpx

from app.infrastructure.faceit.client import FaceitClient
from app.core.config import settings


async def get_httpx_client() -> httpx.AsyncClient:  # type: ignore
    """Создает и предоставляет httpx клиент для работы с Faceit API."""
    async with httpx.AsyncClient(
        base_url=settings.faceit.base_url,
        headers={"Authorization": f"Bearer {settings.faceit.api_key}"},
    ) as client:
        yield client


def get_faceit_client(
    http_client: httpx.AsyncClient = Depends(get_httpx_client),
) -> FaceitClient:
    """Создает экземпляр FaceitClient с внедренным httpx клиентом."""
    return FaceitClient(http_client)
