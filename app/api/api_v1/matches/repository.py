"""Репозиторий для работы с матчами в базе данных."""

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.match import Match
from app.core.models.team import Team


class MatchRepository:
    """Класс для управления жизненным циклом объектов Match в БД."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_match_id(self, match_id: str) -> Match | None:
        """Выполняет поиск конкретного матча по его идентификатору Faceit."""
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

    async def create(self, match: Match) -> Match:
        """Добавляет новый матч в сессию и фиксирует состояние."""
        self.session.add(match)
        await self.session.flush()
        await self.session.refresh(match)
        return match

    async def update(self, match: Match) -> Match:
        """Синхронизирует изменения в существующем матче с базой данных."""
        await self.session.flush()
        await self.session.refresh(match)
        return match
