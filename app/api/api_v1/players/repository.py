"""Репозиторий для работы с игроками в базе данных."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.player import Player


class PlayerRepository:
    """Класс для управления жизненным циклом объектов Player в БД."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_player_id(self, player_id: str) -> Player | None:
        """Выполняет поиск игрока по его уникальному идентификатору Faceit."""
        stmt = select(Player).where(Player.player_id == player_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_nickname(self, nickname: str) -> Player | None:
        """Выполняет поиск игрока по его текущему никнейму."""
        stmt = select(Player).where(Player.nickname == nickname)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, player: Player) -> Player:
        """Регистрирует новый объект игрока в сессии и сохраняет его в БД."""
        self.session.add(player)
        await self.session.flush()
        await self.session.refresh(player)
        return player

    async def update(self, player: Player) -> Player:
        """Синхронизирует изменения существующего объекта игрока с базой данных."""
        await self.session.flush()
        await self.session.refresh(player)
        return player
