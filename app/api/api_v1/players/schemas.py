"""Схемы Pydantic для сущности 'Игрок'."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field, model_validator

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


class MapStatsResponse(BaseModel):
    """Схема статистики игрока по картам."""

    map_name: str = Field(..., alias="label")
    matches: int
    won: int
    lost: int
    winrate: float
    average_kills: float
    average_deaths: float
    average_kd_ratio: float
    average_kr_ratio: float
    hs: float
    adr: float
    rounds: int
    kills: int
    assists: int
    deaths: int
    headshots: int
    total_damage: int
    penta_kills: int

    @model_validator(mode="before")
    @classmethod
    def extract_map_stats(cls, data: Any) -> Any:
        """Парсинг игровой статистики по конкретной карте из данных Faceit."""
        if not isinstance(data, dict) or "stats" not in data:
            return data

        stats: dict = data.get("stats", {})

        matches = int(stats.get("Matches", 0))
        won = int(stats.get("Wins", 0))
        kills = int(stats.get("Kills", 0))
        headshots = int(stats.get("Headshots", 0))

        lost = matches - won
        winrate = round(((won / matches) * 100), 2) if matches > 0 else 0.0
        hs_ratio = round(((headshots / kills) * 100), 2) if kills > 0 else 0.0
        return {
            "map_name": data.get("label"),
            "matches": matches,
            "won": won,
            "lost": lost,
            "winrate": winrate,
            "average_kills": float(stats.get("Average Kills", 0)),
            "average_deaths": float(stats.get("Average Deaths", 0)),
            "average_kd_ratio": float(stats.get("Average K/D Ratio", 0)),
            "average_kr_ratio": float(stats.get("Average K/R Ratio", 0)),
            "hs": hs_ratio,
            "adr": float(stats.get("ADR", 0)),
            "rounds": int(stats.get("Rounds", 0)),
            "kills": kills,
            "assists": int(stats.get("Assists", 0)),
            "deaths": int(stats.get("Deaths", 0)),
            "headshots": headshots,
            "total_damage": int(stats.get("Total Damage", 0)),
            "penta_kills": int(stats.get("Penta Kills", 0)),
        }

    class Config:
        populate_by_name = True


class PlayerCreate(PlayerCSStats, PlayerProfileDetails):
    """Объединенная схема для создания или обновления игрока в базе данных."""

    pass


class PlayerPublic(PlayerCSStats, PlayerProfileDetails):
    """Объединенная схема для вывода игрока."""

    pass


class MapSortField(str, Enum):
    """Доступные поля для сортировки статистики по картам."""

    matches = "matches"
    won = "won"
    lost = "lost"
    winrate = "winrate"
    average_kills = "average_kills"
    average_deaths = "average_deaths"
    average_kd_ratio = "average_kd_ratio"
    average_kr_ratio = "average_kr_ratio"
    hs = "hs"
    adr = "adr"
    rounds = "rounds"
    kills = "kills"
    assists = "assists"
    deaths = "deaths"
    headshots = "headshots"
    total_damage = "total_damage"
    penta_kills = "penta_kills"


class SortDirection(str, Enum):
    """Направление сортировки: по возрастанию или убыванию."""

    asc = "asc"
    desc = "desc"
