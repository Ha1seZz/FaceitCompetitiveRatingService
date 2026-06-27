"""DTO-модели игрока."""

from typing import Any
from datetime import datetime, timezone
from pydantic import BaseModel, model_validator

from app.core.config import settings


class PlayerProfileDetails(BaseModel):
    """Схема основных данных профиля игрока."""

    nickname: str
    country: str | None = None
    verified: bool
    steam_nickname: str | None = None
    steam_id_64: int | None = None
    faceit_url: str
    player_id: str
    friends_count: int
    activated_at: datetime

    @model_validator(mode="before")
    @classmethod
    def prepare_profile(cls, data: Any) -> Any:
        """Трансформирует сырой JSON профиля перед валидацией."""
        if isinstance(data, dict):
            friends = data.get("friends_ids")
            data["friends_count"] = len(friends) if friends is not None else 0

            steam_id = data.get("steam_id_64")
            if steam_id == "" or steam_id is None:
                data["steam_id_64"] = None
            else:
                try:
                    data["steam_id_64"] = int(steam_id)
                except (ValueError, TypeError):
                    data["steam_id_64"] = None

            steam_nick = data.get("steam_nickname")
            if steam_nick == "" or steam_nick is None:
                data["steam_nickname"] = None

            # Конвертация строки в datetime с принудительным UTC
            raw_date = data.get("activated_at")
            if raw_date:
                dt = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
                data["activated_at"] = dt.astimezone(timezone.utc)

            # Формирование локализованной ссылки
            url: str = data.get("faceit_url", "")
            data["faceit_url"] = url.replace("{lang}", settings.faceit.default_language)

        return data


class PlayerCSRating(BaseModel):
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


class PlayerCreate(PlayerCSRating, PlayerProfileDetails):
    """Объединенная схема для создания или обновления игрока в базе данных."""

    pass


class PlayerPublic(PlayerCSRating, PlayerProfileDetails):
    """Публичная схема для отображения полной информации об игроке в API."""

    pass
