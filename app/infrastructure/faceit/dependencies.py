"""Зависимости для обеспечения доступа к Faceit API."""

from fastapi import Depends, Request
import httpx

from app.infrastructure.faceit.client import FaceitClient


async def get_httpx_client(request: Request) -> httpx.AsyncClient:  # type: ignore
    """
    Возвращает синглтон-экземпляр httpx.AsyncClient из состояния приложения.
    Никаких новых соединений на каждый запрос — берем готовое из пула.
    """
    return request.app.state.httpx_client


def get_faceit_client(
    http_client: httpx.AsyncClient = Depends(get_httpx_client),
) -> FaceitClient:
    """Создает экземпляр FaceitClient с внедренным httpx клиентом."""
    return FaceitClient(http_client)
