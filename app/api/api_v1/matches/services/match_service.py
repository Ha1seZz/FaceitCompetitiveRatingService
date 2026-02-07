"""Сервис для управления бизнес-логикой матчей."""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import Match, Team, MatchPlayer
from app.api.api_v1.matches.repository import MatchRepository
from app.api.api_v1.matches.schemas import MatchCreate


class MatchService:
    """Use-case слой для матчей: синхронизация Faceit -> БД и запросы к локальным данным."""

    def __init__(self, session: AsyncSession, repository: MatchRepository):
        self.session = session
        self.repository = repository

    @staticmethod
    def _build_teams(raw_list: list[dict]) -> list[Team]:
        """Строит SQLAlchemy Team/MatchPlayer из валидированных данных (teams_raw)."""
        teams: list[Team] = []
        for team_data in raw_list:
            players_data = team_data.get("roster", [])
            payload = {k: v for k, v in team_data.items() if k != "roster"}

            team = Team(**payload)
            team.players = [MatchPlayer(**p) for p in players_data]
            teams.append(team)

        return teams

    async def create_or_update_from_faceit(self, match_data: dict) -> Match:
        """Upsert матча: валидирует данные Faceit и синхронизирует их с БД."""
        # Валидация и трансформация данных через Pydantic
        validated = MatchCreate(**match_data)
        data = validated.model_dump()
        teams_raw = data.pop("teams")

        match = await self.repository.get_by_match_id(data["match_id"])

        if match:  # Обновление существующего матча
            for key, value in data.items():
                setattr(match, key, value)
            match.teams = self._build_teams(teams_raw)
            match = await self.repository.update(match)
        else:  # Создание новой записи
            new_match = Match(**data)
            new_match.teams = self._build_teams(teams_raw)
            match = await self.repository.create(new_match)
        return match

    async def get_matches(self, limit: int, offset: int) -> list[Match]:
        """Возвращает список матчей из локальной БД с пагинацией."""
        return await self.repository.get_all(limit=limit, offset=offset)

    async def get_finished_matches_by_region(self, region: str) -> list[Match]:
        """Возвращает только FINISHED матчи для заданного региона."""
        matches = await self.repository.get_all_by_region(region)
        return [m for m in matches if m.status == "FINISHED"]

    async def delete_match(self, match_id: str) -> None:
        """Удаляет матч; если матч не найден — кидает 404."""
        success = await self.repository.delete_match(match_id=match_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Матч с ID {match_id} не найден в базе данных.",
            )
