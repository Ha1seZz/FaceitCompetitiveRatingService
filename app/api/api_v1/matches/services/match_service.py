"""Сервис для работы с матчами."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.api_v1.matches.schemas import MatchCreate
from repository import MatchRepository
from app.core.models import Match


class MatchService:
    """Сервис для бизнес-логики работы с матчами."""

    def __init__(self, session: AsyncSession, repository: MatchRepository):
        self.session = session
        self.repository = repository

    async def create_or_update_from_faceit(self, match_data: dict) -> Match:
        """Создать или обновить матч из данных Faceit API."""
        validated = MatchCreate(**match_data)
        data = validated.model_dump()

        async with self.session.begin():
            existing_match = await self.repository.get_by_match_id(data["match_id"])

            if existing_match:
                for key, value in data.items():
                    setattr(existing_match, key, value)
                match = await self.repository.update(existing_match)
            else:
                new_match = Match(**data)
                match = await self.repository.create(new_match)

        return match

    async def get_finished_matches_by_region(self, region: str) -> list[Match]:
        """Получить завершенные матчи региона."""
        matches = await self.repository.get_all_by_region(region)
        return [m for m in matches if m.status == "FINISHED"]
