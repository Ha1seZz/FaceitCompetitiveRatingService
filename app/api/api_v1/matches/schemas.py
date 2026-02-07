"""Схемы Pydantic для сущности 'Матч'."""

from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, Field, model_validator

from app.core.config import settings


class MatchPlayerSchema(BaseModel):
    """Схема данных игрока в конкретном матче."""

    player_id: str
    nickname: str
    membership: str
    game_player_id: int
    game_player_name: str
    game_skill_level: int = 0


class TeamSchema(BaseModel):
    """Схема данных команды внутри матча."""

    faction_id: str
    name: str
    roster: list[MatchPlayerSchema] = Field(alias="players")
    win_probability: float | None = None
    average_skill_level: int | None = None
    rating: int | None = None

    class Config:
        from_attributes = True
        populate_by_name = True


class MatchDetails(BaseModel):
    """Основная схема данных матча."""

    match_id: str
    region: str
    status: str

    competition_id: str
    competition_type: str
    competition_name: str
    organizer_id: str

    teams: list[TeamSchema]

    maps: list[str]
    location: str

    winner: str
    score: dict[str, int]

    configured_at: datetime
    started_at: datetime
    finished_at: datetime

    best_of: int
    calculate_elo: bool
    faceit_url: str

    @model_validator(mode="before")
    @classmethod
    def prepare_match_data(cls, data: Any) -> Any:
        """Комплексный трансформатор сырых данных матча."""
        if not isinstance(data, dict):
            return data

        # Трансформация команд
        raw_teams = data.get("teams", {})
        teams_list = []
        for faction_key in ("faction1", "faction2"):
            t = raw_teams.get(faction_key, {})
            if not t:
                continue

            stats = t.get("stats", {})
            teams_list.append(
                {
                    "faction_id": t.get("faction_id"),
                    "name": t.get("name"),
                    "players": [
                        {
                            "player_id": p.get("player_id"),
                            "nickname": p.get("nickname"),
                            "membership": p.get("membership"),
                            "game_player_id": p.get("game_player_id"),
                            "game_player_name": p.get("game_player_name"),
                            "game_skill_level": p.get("game_skill_level", 0),
                        }
                        for p in t.get("roster", [])
                    ],
                    "win_probability": stats.get("winProbability"),
                    "average_skill_level": stats.get("skillLevel", {}).get("average"),
                    "rating": stats.get("rating"),
                }
            )
        data["teams"] = teams_list

        # Конвертация строк в datetime с принудительным UTC
        for field in ["configured_at", "started_at", "finished_at"]:
            value = data.get(field)
            if value in (None, 0):
                data[field] = datetime.now(timezone.utc)
            elif isinstance(value, (int, float)):
                data[field] = datetime.fromtimestamp(value, tz=timezone.utc)

        # Голосование
        voting = data.get("voting", {})
        data["maps"] = voting.get("map", {}).get("pick", [])
        loc_picks = voting.get("location", {}).get("pick", [])
        data["location"] = loc_picks[0] if loc_picks else "unknown"

        # Результаты
        results = data.get("results", {})
        data["winner"] = results.get("winner", "TBD")
        data["score"] = results.get("score", {})

        # Формирование локализованной ссылки
        url: str = data.get("faceit_url", "")
        data["faceit_url"] = url.replace("{lang}", settings.faceit.default_language)

        return data


class MatchStats(BaseModel):
    """Дополнительная статистика матча (расширяемая)."""

    pass


class MatchCreate(MatchDetails, MatchStats):
    """Объединенная схема для создания или синхронизации матча в БД."""

    pass


class MatchPublic(MatchStats, MatchDetails):
    """Объединенная схема для вывода матча."""

    pass
