"""Сервис для работы с игроками."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.api_v1.players.schemas import PlayerCreate
from app.api.api_v1.players.repository import PlayerRepository
from app.core.models import Player


class PlayerService:
    """Сервис для бизнес-логики работы с игроками."""

    def __init__(self, session: AsyncSession, repository: PlayerRepository):
        self.session = session
        self.repository = repository

    async def create_or_update_from_faceit(self, player_data: dict) -> Player:
        """Создать или обновить матч из данных Faceit API."""
        validated = PlayerCreate(**player_data)
        data = validated.model_dump()

        async with self.session.begin():
            player = await self.repository.get_by_player_id(data["player_id"])

            if player:
                for key, value in data.items():
                    setattr(player, key, value)
                player = await self.repository.update(player)
            else:
                new_player = Player(**data)
                player = await self.repository.create(new_player)

        return player
