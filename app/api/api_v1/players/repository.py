"""Репозиторий для работы с игроками в БД."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.player import Player


class PlayerRepository:
    """Репозиторий для CRUD операций с игроками."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_player_id(self, player_id: str) -> Player | None:
        """Получить игрока по ID."""
        stmt = select(Player).where(Player.player_id == player_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_nickname(self, nickname: str) -> Player | None:
        """Получить игрока по никнейму."""
        stmt = select(Player).where(Player.nickname == nickname)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, player: Player) -> Player:
        """Добавить игрока в БД."""
        self.session.add(player)
        await self.session.flush()
        await self.session.refresh(player)
        return player

    async def update(self, player: Player) -> Player:
        """Обновить существующий игрока."""
        await self.session.flush()
        await self.session.refresh(player)
        return player
