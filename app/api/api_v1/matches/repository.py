"""Репозиторий для работы с матчами в базе данных."""

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import Match, Team


class MatchRepository:
    """Класс для управления жизненным циклом объектов Match в БД."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, match: Match) -> Match:
        """Добавляет новый матч в сессию и фиксирует состояние."""
        self.session.add(match)
        await self.session.flush()
        await self.session.refresh(match)
        return match

    async def get_all(self, limit: int, offset: int) -> list[Match]:
        """Извлекает все матчи из базы данных."""
        stmt = select(Match).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_match_id(self, match_id: str) -> Match | None:
        """Возвращает матч по match_id вместе с командами и игроками (selectinload, без N+1)."""
        stmt = (
            select(Match)
            .where(Match.match_id == match_id)
            .options(selectinload(Match.teams).selectinload(Team.players))
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_all_by_region(self, region: str) -> list[Match]:
        """Извлекает список всех матчей, принадлежащих конкретному региону (например, EU, US)."""
        stmt = (
            select(Match)
            .where(Match.region == region)
            .options(selectinload(Match.teams).selectinload(Team.players))
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def update(self, match: Match) -> Match:
        """Синхронизирует изменения в существующем матче с базой данных."""
        await self.session.flush()
        await self.session.refresh(match)
        return match

    async def delete_match(self, match_id: str) -> bool:
        """
        Удаляет матч из базы данных по его match_id.
        Возвращает True, если матч был найден и удален, иначе False.
        """
        match = await self.session.get(Match, match_id)
        if match:
            await self.session.delete(match)
            return True
        return False
