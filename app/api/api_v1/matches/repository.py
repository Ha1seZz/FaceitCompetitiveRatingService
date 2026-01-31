"""Репозиторий для работы с матчами в БД."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.match import Match


class MatchRepository:
    """Репозиторий для CRUD операций с матчами."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_match_id(self, match_id: str) -> Match | None:
        """Получить матч по ID."""
        stmt = select(Match).where(Match.match_id == match_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_by_region(self, region: str) -> list[Match]:
        """Получить все матчи региона."""
        stmt = select(Match).where(Match.region == region)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, match: Match) -> Match:
        """Добавить матч в БД."""
        self.session.add(match)
        await self.session.flush()
        await self.session.refresh(match)
        return match

    async def update(self, match: Match) -> Match:
        """Обновить существующий матч."""
        await self.session.flush()
        await self.session.refresh(match)
        return match
