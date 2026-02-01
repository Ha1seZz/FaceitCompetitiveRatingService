"""Сервис для управления бизнес-логикой матчей."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.api_v1.matches.schemas import MatchCreate
from app.api.api_v1.matches.repository import MatchRepository
from app.core.models.team import Team
from app.core.models import Match


class MatchService:
    """Класс-сервис для обработки высокоуровневых операций с матчами."""

    def __init__(self, session: AsyncSession, repository: MatchRepository):
        self.session = session
        self.repository = repository

    async def create_or_update_from_faceit(self, match_data: dict) -> Match:
        """Синхронизирует данные матча, полученные из внешнего API, с базой данных."""
        # Валидация и трансформация данных через Pydantic
        validated = MatchCreate(**match_data)
        data = validated.model_dump()

        teams_data = data.pop("teams")

        async with self.session.begin():
            existing_match = await self.repository.get_by_match_id(data["match_id"])

            if existing_match:  # Обновление существующего матча
                for key, value in data.items():
                    setattr(existing_match, key, value)
                existing_match.teams = [Team(**t) for t in teams_data]
                match = await self.repository.update(existing_match)
            else:  # Создание новой записи
                new_match = Match(**data)
                new_match.teams = [Team(**t) for t in teams_data]
                match = await self.repository.create(new_match)

            await self.session.refresh(match, attribute_names=["teams"])

        return match

    async def get_finished_matches_by_region(self, region: str) -> list[Match]:
        """Возвращает список только завершенных матчей для указанного региона."""
        matches = await self.repository.get_all_by_region(region)
        return [m for m in matches if m.status == "FINISHED"]
