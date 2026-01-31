"""Модуль клиента для взаимодействия с Faceit Data API."""

import httpx
from app.core.exceptions import ExternalServiceUnavailable, FaceitEntityNotFound


class FaceitClient:
    """Асинхронный клиент для выполнения запросов к API Faceit."""

    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    async def get_player(self, nickname: str) -> dict:
        """Запрашивает данные игрока по его никнейму."""
        response = await self.client.get(
            "/players",
            params={"nickname": nickname},
        )

        if response.status_code == 404:
            raise FaceitEntityNotFound("Player not found on Faceit")

        if response.status_code >= 500:
            raise ExternalServiceUnavailable("Faceit API unavailable")

        response.raise_for_status()
        return response.json()

    async def get_match(self, match_id: str) -> dict:
        """Запрашивает детальную информацию о матче по его уникальному ID."""
        response = await self.client.get(f"/matches/{match_id}")

        if response.status_code == 404:
            raise FaceitEntityNotFound("Match not found on Faceit")

        if response.status_code >= 500:
            raise ExternalServiceUnavailable("Faceit API unavailable")

        response.raise_for_status()
        return response.json()
