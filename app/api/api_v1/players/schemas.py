"""Схемы Pydantic для сущности 'Игрок'."""

from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, model_validator

from app.core.config import settings


class PlayerProfileDetails(BaseModel):
    """Схема основных данных профиля игрока."""

    nickname: str
    country: str
    verified: bool
    steam_nickname: str
    steam_id_64: int
    faceit_url: str
    player_id: str
    friends_count: int
    activated_at: datetime

    @model_validator(mode="before")
    @classmethod
    def prepare_profile(cls, data: Any) -> Any:
        """Трансформирует сырой JSON профиля перед валидацией."""
        if isinstance(data, dict):
            data["friends_count"] = len(data.get("friends_ids"))  # Подсчет друзей

            # Конвертация строки в datetime с принудительным UTC
            raw_date = data.get("activated_at")
            dt = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
            data["activated_at"] = dt.astimezone(timezone.utc)

            # Формирование локализованной ссылки
            url: str = data.get("faceit_url", "")
            data["faceit_url"] = url.replace("{lang}", settings.faceit.default_language)
        return data


class PlayerCSStats(BaseModel):
    """Схема игровой статистики Counter-Strike."""

    region: str
    skill_level: int
    faceit_elo: int

    @model_validator(mode="before")
    @classmethod
    def extract_cs_stats(cls, data: Any) -> Any:
        """Извлекает специфичные для CS данные из общего словаря игр Faceit."""
        if isinstance(data, dict):
            games: dict = data.get("games", {})
            cs_info = games.get("cs2") or games.get("csgo") or {}

            data["region"] = cs_info.get("region", "")
            data["skill_level"] = cs_info.get("skill_level", 0)
            data["faceit_elo"] = cs_info.get("faceit_elo", 0)

        return data


class PlayerCreate(PlayerCSStats, PlayerProfileDetails):
    """Объединенная схема для создания или обновления игрока в базе данных."""

    pass


class PlayerPublic(PlayerCSStats, PlayerProfileDetails):
    """Объединенная схема для вывода игрока."""

    pass
