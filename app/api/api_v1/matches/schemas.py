"""Схемы Pydantic для сущности 'Матч'."""

from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, model_validator

from app.core.config import settings


class TeamSchema(BaseModel):
    """Схема данных команды внутри матча."""

    faction_id: str
    name: str
    roster: list[dict[str, Any]]
    win_probability: float | None = None
    average_skill_level: int | None = None
    rating: int | None = None


class MatchDetails(BaseModel):
    """Основная схема данных матча."""

    match_id: str
    region: str
    status: str

    # Информация о соревновании
    competition_id: str
    competition_type: str
    competition_name: str
    organizer_id: str

    # Команды
    teams: list[TeamSchema]

    # Данные голосования
    maps: list[str]
    location: str

    # Результат игры
    winner: str
    score: dict[str, int]

    # Временные метки (UTC)
    configured_at: datetime
    started_at: datetime
    finished_at: datetime

    # Конфигурация и метаданные
    best_of: int
    calculate_elo: bool
    faceit_url: str

    @model_validator(mode="before")
    @classmethod
    def prepare_match_data(cls, data: Any) -> Any:
        """Комплексный трансформатор сырых данных матча."""
        if isinstance(data, dict):
            # Превращаем объект factions в список для связи
            raw_teams = data.get("teams", {})
            teams_list = []
            for faction_key in ["faction1", "faction2"]:
                t = raw_teams.get(faction_key, {})
                stats = t.get("stats", {})
                teams_list.append(
                    {
                        "faction_id": t.get("faction_id"),
                        "name": t.get("name"),
                        "roster": t.get("roster", []),
                        "win_probability": stats.get("winProbability"),
                        "average_skill_level": stats.get("skillLevel", {}).get(
                            "average"
                        ),
                        "rating": stats.get("rating"),
                    }
                )
            data["teams"] = teams_list

            # Конвертация строк в datetime с принудительным UTC
            date_fields = ["configured_at", "started_at", "finished_at"]
            for field in date_fields:
                value = data.get(field)
                if value is None:
                    continue

                if isinstance(value, (int, float)):
                    data[field] = datetime.fromtimestamp(value, tz=timezone.utc)
                elif isinstance(value, str):
                    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
                    data[field] = dt.astimezone(timezone.utc)

            # Раскрытие структуры голосования
            voting = data.get("voting", {})

            # Извлечение карты
            map_info = voting.get("map", {})
            data["maps"] = map_info.get("pick", [])

            # Извлечение локации (сервера)
            loc_info = voting.get("location", {})
            data["location"] = loc_info.get("pick", ["unknown"])[0]

            # Упрощение структуры результатов
            results = data.get("results", {})
            data["winner"] = results.get("winner", "")
            data["score"] = results.get("score", {})

            # Формирование локализованной ссылки
            url: str = data.get("faceit_url", "")
            data["faceit_url"] = url.replace("{lang}", settings.faceit.default_language)

        return data


class MatchStats(BaseModel):
    """Дополнительная статистика матча (расширяемая)."""

    ...


class MatchCreate(MatchDetails, MatchStats):
    """Объединенная схема для создания или синхронизации матча в БД."""

    pass
