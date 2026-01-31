from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, model_validator

from app.core.config import settings


class MatchDetails(BaseModel):
    match_id: str
    region: str
    status: str

    # Информация о соревновании
    competition_id: str
    competition_type: str
    competition_name: str
    organizer_id: str

    # Команды
    teams: dict[str, Any]

    # Голосование
    map: str
    location: str

    # Результат
    winner: str
    score: dict[str, int]

    # Временные метки
    configured_at: datetime
    started_at: datetime
    finished_at: datetime

    # Дополнительные данные
    best_of: int
    calculate_elo: bool
    faceit_url: str

    @model_validator(mode="before")
    @classmethod
    def prepare_profile(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Конвертирует строки в datetime и принудительно ставит UTC
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

            # Безопасное извлечение
            voting = data.get("voting", {})
            map_info = voting.get("map", {})
            data["map"] = map_info.get("pick", ["unknown"])[0]

            loc_info = voting.get("location", {})
            data["location"] = loc_info.get("pick", ["unknown"])[0]

            results = data.get("results", {})
            data["winner"] = results.get("winner", "none")
            data["score"] = results.get("score", {})

            # Формирует рабочую ссылку, заменяя плейсхолдер на русский язык
            url: str = data.get("faceit_url", "")
            data["faceit_url"] = url.replace("{lang}", settings.faceit.default_language)

        return data


class MatchStats(BaseModel):
    ...


class MatchCreate(MatchDetails, MatchStats):
    pass
