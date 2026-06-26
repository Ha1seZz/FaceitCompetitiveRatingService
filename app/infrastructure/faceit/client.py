"""Модуль клиента для взаимодействия с Faceit Data API."""

import asyncio

import httpx
from loguru import logger
from app.core.exceptions import ExternalServiceUnavailable, FaceitEntityNotFound


class FaceitClient:
    """Асинхронный клиент для выполнения запросов к API Faceit."""

    _global_semaphore = asyncio.Semaphore(5)

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

    async def get_player_stats(
        self,
        player_id: str,
        game_id: str = "cs2",
        max_matches: int = 30,
    ) -> dict:
        """Запрашивает необработанную статистику игрока."""
        response = await self.client.get(
            f"/players/{player_id}/games/{game_id}/stats",
            params={"limit": max_matches},
        )
        return await self._handle_response(response, "Player stats")

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
        max_matches: int = 500,
        start_offset: int = 0,
    ) -> list[dict]:
        """Загружает историю матчей игрока из Faceit."""
        limit = 100
        all_matches: list[dict] = []

        for offset in range(start_offset, max_matches, limit):
            async with self._global_semaphore:
                logger.debug(
                    "Запрос пачки матчей (offset={offset}) для {player_id}",
                    offset=offset,
                    player_id=player_id,
                )
                try:
                    response = await self.client.get(
                        f"/players/{player_id}/history",
                        params={"game": game, "offset": offset, "limit": limit},
                    )
                    data = await self._handle_response(response, "Match history")
                    page = data.get("items", []) or []
                except Exception as e:
                    logger.error(
                        "Ошибка при загрузке истории матчей для {player_id} на offset={offset}: {e}",
                        player_id=player_id,
                        offset=offset,
                        e=e,
                    )
                    raise

            if not page:
                break

            all_matches.extend(page)

            if len(page) < limit:
                break

        return all_matches
