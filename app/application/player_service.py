"""Сервис для управления бизнес-логикой игроков."""

from fastapi import HTTPException, status

from app.schemas import PlayerCreate
from app.infrastructure.db.repositories.player_repository import PlayerRepository
from app.infrastructure.faceit.client import FaceitClient
from app.infrastructure.db.models import Player


class PlayerService:
    """Класс-сервис для обработки операций с игроками."""

    def __init__(
        self,
        repository: PlayerRepository,
        faceit_client: FaceitClient,
    ):
        self.repository = repository
        self.faceit_client = faceit_client

    async def create_or_update_from_faceit(self, player_data: dict) -> Player:
        """Синхронизирует данные игрока, полученные из внешнего API, с базой данных."""
        # Валидация и трансформация данных через Pydantic
        validated = PlayerCreate(**player_data)
        data = validated.model_dump()

        player = await self.repository.get_by_player_id(data["player_id"])

        if player:  # Обновление существующего игрока
            for key, value in data.items():
                setattr(player, key, value)
            player = await self.repository.update(player)
        else:  # Создание новой записи
            new_player = Player(**data)
            player = await self.repository.create(new_player)

        return player

    async def get_or_create_player(self, nickname: str) -> Player:
        player = await self.repository.get_by_nickname(nickname)  # Ищем локально

        if player:
            return player

        # Иначе, тянем Faceit
        player_data = await self.faceit_client.get_player(nickname)

        return await self.create_or_update_from_faceit(player_data=player_data)

    async def get_players(self, limit: int, offset: int) -> list[Player]:
        """Получает список всех игроков."""
        return await self.repository.get_all(limit=limit, offset=offset)

    async def delete_player(self, player_id: str) -> None:
        """Проверяет результат удаления и вызывает исключение, если игрок не найден."""
        success = await self.repository.delete_player(player_id=player_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Игрок с ID {player_id} не найден в базе данных.",
            )
