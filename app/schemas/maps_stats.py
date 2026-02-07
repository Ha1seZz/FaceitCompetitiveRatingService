"""DTO-модели статистики игрока по картам."""

from typing import Any
from pydantic import BaseModel, ConfigDict, model_validator


class MapStatsBase(BaseModel):
    """Базовая структура статистики игрока на конкретной карте."""

    map_name: str
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

        s: dict = data.get("stats", {})

        m = int(s.get("Matches", 0))
        w = int(s.get("Wins", 0))
        k = int(s.get("Kills", 0))
        hs = int(s.get("Headshots", 0))

        lost = m - w
        winrate = round(((w / m) * 100), 2) if m > 0 else 0.0
        hs_ratio = round(((hs / k) * 100), 2) if k > 0 else 0.0
        return {
            "map_name": data.get("label"),
            "matches": m,
            "won": w,
            "lost": lost,
            "winrate": winrate,
            "average_kills": float(s.get("Average Kills", 0)),
            "average_deaths": float(s.get("Average Deaths", 0)),
            "average_kd_ratio": float(s.get("Average K/D Ratio", 0)),
            "average_kr_ratio": float(s.get("Average K/R Ratio", 0)),
            "hs": hs_ratio,
            "adr": float(s.get("ADR", 0)),
            "rounds": int(s.get("Rounds", 0)),
            "kills": k,
            "assists": int(s.get("Assists", 0)),
            "deaths": int(s.get("Deaths", 0)),
            "headshots": hs,
            "total_damage": int(s.get("Total Damage", 0)),
            "penta_kills": int(s.get("Penta Kills", 0)),
        }


class MapStatsResponse(MapStatsBase):
    """Схема ответа API со статистикой по картам."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class MapStatsCreate(MapStatsBase):
    """Схема для создания записей статистики в базе данных."""

    pass
