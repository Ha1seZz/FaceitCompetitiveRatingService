"""DTO-модели статистики игрока по картам."""

from pydantic import BaseModel, ConfigDict


class MapStatsResponse(BaseModel):
    """Схема ответа API со статистикой по картам."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

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
