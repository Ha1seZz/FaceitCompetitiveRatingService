"""Сервис для управления бизнес-логикой игроков."""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.api_v1.players.schemas import (
    MapSortField,
    MapStatsResponse,
    PlayerCreate,
    SortDirection,
)
from app.api.api_v1.players.repository import PlayerRepository
from app.core.models import Player


class PlayerService:
    """Класс-сервис для обработки высокоуровневых операций с игроками."""

    def __init__(self, session: AsyncSession, repository: PlayerRepository):
        self.session = session
        self.repository = repository

    async def create_or_update_from_faceit(self, player_data: dict) -> Player:
        """Синхронизирует данные игрока, полученные из внешнего API, с базой данных."""
        # Валидация и трансформация данных через Pydantic
        validated = PlayerCreate(**player_data)
        data = validated.model_dump()

        async with self.session.begin():
            player = await self.repository.get_by_player_id(data["player_id"])

            if player:  # Обновление существующего игрока
                for key, value in data.items():
                    setattr(player, key, value)
                player = await self.repository.update(player)
            else:  # Создание новой записи
                new_player = Player(**data)
                player = await self.repository.create(new_player)

        return player

    async def get_players(self, limit: int, offset: int) -> list[Player]:
        """Получает список всех игроков."""
        return await self.repository.get_all(limit=limit, offset=offset)

    async def transform_maps_stats(
        self,
        raw_data: dict,
        sort_by: MapSortField,
        sort_direction: SortDirection,
    ) -> list[MapStatsResponse]:
        """Преобразует сырые сегменты в отсортированный список валидированных моделей."""
        segments = raw_data.get("segments", [])

        stats = [
            MapStatsResponse(**segment)
            for segment in segments
            if segment.get("type") == "Map"
        ]

        reverse = sort_direction == SortDirection.desc
        stats.sort(key=lambda x: getattr(x, sort_by.value), reverse=reverse)

        return stats

    async def delete_player(self, player_id: str) -> None:
        """Проверяет результат удаления и вызывает исключение, если игрок не найден."""
        success = await self.repository.delete_player(player_id=player_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Игрок с ID {player_id} не найден в базе данных.",
            )
