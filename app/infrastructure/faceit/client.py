"""Модуль клиента для взаимодействия с Faceit Data API."""

import logging
from typing import AsyncGenerator

import httpx
from loguru import logger
from tenacity import (
    retry,
    wait_exponential,
    stop_after_attempt,
    retry_if_exception_type,
    before_sleep_log,
)
from aiolimiter import AsyncLimiter

from app.core.exceptions import ExternalServiceUnavailable, FaceitEntityNotFound


class FaceitClient:
    """Асинхронный клиент для выполнения запросов к API Faceit."""

    _rate_limiter = AsyncLimiter(max_rate=5, time_period=1)

    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    @retry(
        wait=wait_exponential(multiplier=2, min=4, max=60),
        stop=stop_after_attempt(5),
        retry=retry_if_exception_type((httpx.RequestError, ExternalServiceUnavailable)),
        reraise=True,
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def _execute_request(
        self,
        endpoint: str,
        params: dict | None,
        entity_name: str,
    ) -> dict:
        """Единая точка входа для всех запросов."""

        async with self._rate_limiter:
            response = await self.client.get(endpoint, params=params)

        if response.status_code == 404:
            raise FaceitEntityNotFound(f"{entity_name} not found on Faceit")

        if response.status_code == 429:
            raise ExternalServiceUnavailable(
                f"Faceit API rate limit exceeded (429) for {entity_name}"
            )

        if response.status_code >= 500:
            raise ExternalServiceUnavailable(
                f"Faceit API unavailable ({response.status_code}) for {entity_name}"
            )

        response.raise_for_status()
        return response.json()

    async def get_player(self, nickname: str) -> dict:
        """Запрашивает данные игрока по его никнейму."""
        return await self._execute_request(
            "/players",
            params={"nickname": nickname},
            entity_name="Player",
        )

    async def get_player_stats(
        self,
        player_id: str,
        game_id: str = "cs2",
        max_matches: int = 30,
    ) -> dict:
        """Запрашивает необработанную статистику игрока."""
        return await self._execute_request(
            f"/players/{player_id}/games/{game_id}/stats",
            params={"limit": max_matches},
            entity_name="Player stats",
        )

    async def get_match(self, match_id: str) -> dict:
        """Запрашивает детальную информацию о матче по его уникальному ID."""
        return await self._execute_request(
            f"/matches/{match_id}",
            params=None,
            entity_name="Match",
        )

    async def get_player_maps_stats_raw(
        self,
        player_id: str,
        game_id: str = "cs2",
    ) -> dict:
        """Запрашивает необработанную статистику игрока по каждой карте."""
        return await self._execute_request(
            f"/players/{player_id}/stats/{game_id}",
            params=None,
            entity_name="Stats",
        )

    async def get_player_match_history(
        self,
        player_id: str,
        game: str = "cs2",
        max_matches: int = 500,
        start_offset: int = 0,
    ) -> AsyncGenerator[list[dict], None]:
        """Загружает историю матчей игрока из Faceit."""
        limit = 100

        for offset in range(start_offset, max_matches, limit):
            logger.debug(
                "Запрос пачки матчей (offset={offset}) для {player_id}",
                offset=offset,
                player_id=player_id,
            )
            try:
                data = await self._execute_request(
                    f"/players/{player_id}/history",
                    params={"game": game, "offset": offset, "limit": limit},
                    entity_name="Match history",
                )
                page = data.get("items", []) or []
            except Exception as e:
                logger.error(
                    "Загрузка истории оборвалось на offset={offset} для {player_id}. Предыдущие пачки сохранены. Ошибка: {e}",
                    offset=offset,
                    player_id=player_id,
                    e=e,
                )
                raise

            if not page:
                break

            yield page

            if len(page) < limit:
                break
