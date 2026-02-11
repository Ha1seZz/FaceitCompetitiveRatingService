"""Модуль клиента для взаимодействия с Faceit Data API."""

import httpx
from app.core.exceptions import ExternalServiceUnavailable, FaceitEntityNotFound


class FaceitClient:
    """Асинхронный клиент для выполнения запросов к API Faceit."""

    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    async def _handle_response(
        self,
        response: httpx.Response,
        entity_name: str,
    ) -> dict:
        """Централизованная обработка ответов Faceit."""
        if response.status_code == 404:
            raise FaceitEntityNotFound(f"{entity_name} not found on Faceit")

        if response.status_code >= 500:
            raise ExternalServiceUnavailable("Faceit API unavailable")

        response.raise_for_status()
        return response.json()

    async def get_player(self, nickname: str) -> dict:
        """Запрашивает данные игрока по его никнейму."""
        response = await self.client.get(
            "/players",
            params={"nickname": nickname},
        )
        return await self._handle_response(response, "Player")

    async def get_match(self, match_id: str) -> dict:
        """Запрашивает детальную информацию о матче по его уникальному ID."""
        response = await self.client.get(f"/matches/{match_id}")
        return await self._handle_response(response, "Match")

    async def get_player_maps_stats_raw(
        self,
        player_id: str,
        game_id: str = "cs2",
    ) -> dict:
        """Запрашивает необработанную статистику игрока по каждой карте."""
        response = await self.client.get(f"/players/{player_id}/stats/{game_id}")
        return await self._handle_response(response, "Stats")

    async def get_player_match_history(
        self,
        player_id: str,
        game: str = "cs2",
        max_matches: int = 1000,
    ) -> list[dict]:
        """Загружает историю матчей игрока из Faceit."""
        all_matches: list[dict] = []
        limit = 100
        offset = 0

        while offset < max_matches:
            response = await self.client.get(
                f"/players/{player_id}/history",
                params={"game": game, "offset": offset, "limit": limit},
            )

            data = await self._handle_response(response, "Match history")
            items = data.get("items", [])

            if not items:
                break

            all_matches.extend(items)

            if len(items) < limit:
                break

            offset += limit

        return all_matches
