"""DTO-модель для аналитического ответа статистики игрока."""

from pydantic import BaseModel


class PlayerStatsInsight(BaseModel):
    """Агрегированная статистика игрока за последние матчи."""

    player_id: str
    matches_analyzed: int
    winrate: float
    avg_kills: float
    avg_deaths: float
    avg_assists: float
    avg_damage: float
    kd_ratio: float
    kr_ratio: float
    headshots_percent: float
    adr: float
