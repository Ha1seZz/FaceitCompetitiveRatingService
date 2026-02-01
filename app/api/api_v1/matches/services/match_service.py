"""Сервис для управления бизнес-логикой матчей."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.match_player import MatchPlayer
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
        teams_raw = data.pop("teams")

        async with self.session.begin():
            match = await self.repository.get_by_match_id(data["match_id"])

            def build_teams(raw_list):
                new_teams = []
                for t in raw_list:
                    players_data = t.pop("roster", [])
                    team_obj = Team(**t)
                    team_obj.players = [MatchPlayer(**p) for p in players_data]
                    new_teams.append(team_obj)
                return new_teams

            if match:  # Обновление существующего матча
                for key, value in data.items():
                    setattr(match, key, value)
                match.teams = build_teams(teams_raw)
                await self.repository.update(match)
            else:  # Создание новой записи
                new_match = Match(**data)
                new_match.teams = build_teams(teams_raw)
                await self.repository.create(new_match)

            await self.session.refresh(match, attribute_names=["teams"])
        return match

    async def get_finished_matches_by_region(self, region: str) -> list[Match]:
        """Возвращает список только завершенных матчей для указанного региона."""
        matches = await self.repository.get_all_by_region(region)
        return [m for m in matches if m.status == "FINISHED"]
