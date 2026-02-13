"""Репозиторий для работы с игроками в базе данных."""

from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import Player
from app.schemas import MatchHistoryMeta


class PlayerRepository:
    """Класс для управления жизненным циклом объектов Player в БД."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, player: Player) -> Player:
        """Сохраняет нового игрока в базе данных."""
        self.session.add(player)
        await self.session.flush()
        await self.session.refresh(player)
        return player

    async def get_all(self, limit: int, offset: int) -> list[Player]:
        """Возвращает список игроков с поддержкой пагинации."""
        stmt = select(Player).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

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

    async def get_match_history_meta(self, player_id) -> MatchHistoryMeta | None:
        """Вернуть мету кэша истории матчей игрока."""
        stmt = select(Player.player_id, Player.match_history_updated_at).where(
            Player.player_id == player_id
        )
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None

        pid, updated_at = row
        return MatchHistoryMeta(player_id=pid, updated_at=updated_at)

    async def get_match_history_updated_at(self, player_id: str) -> datetime | None:
        """Вернуть timestamp обновления истории матчей (или None, если игрок не найден/не обновлялся)."""
        stmt = select(Player.match_history_updated_at).where(
            Player.player_id == player_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def set_match_history_updated_at(
        self,
        player_id: str,
        updated_at: datetime,
    ) -> bool:
        """Установить timestamp обновления истории матчей."""
        player = await self.session.get(Player, player_id)
        if player:
            player.match_history_updated_at = updated_at
            return True
        return False

    async def update(self, player: Player) -> Player:
        """Синхронизирует изменения существующего объекта игрока с базой данных."""
        await self.session.flush()
        await self.session.refresh(player)
        return player

    async def delete_player(self, player_id: str) -> bool:
        """
        Удаляет игрока из базы данных по его player_id.
        Возвращает True, если игрок был найден и удален, иначе False.
        """
        player = await self.session.get(Player, player_id)
        if player:
            await self.session.delete(player)
            return True
        return False
