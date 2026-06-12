"""Доменные snapshot-структуры для анализа статистики игрока по картам."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class MapStatDomainModel:
    """Полная доменная модель статистики по карте."""

    map_name: str
    player_id: str
    matches: int = 0
    won: int = 0
    lost: int = 0
    winrate: float = 0.0
    average_kills: float = 0.0
    average_deaths: float = 0.0
    average_kd_ratio: float = 0.0
    average_kr_ratio: float = 0.0
    hs: float = 0.0
    adr: float = 0.0
    rounds: int = 0
    kills: int = 0
    assists: int = 0
    deaths: int = 0
    headshots: int = 0
    total_damage: int = 0
    penta_kills: int = 0
    id: int | None = None
    updated_at: datetime | None = None


@dataclass(frozen=True)
class MapStatSnapshot:
    """Снимок статистики игрока по одной карте."""

    map_name: str
    winrate: float
    matches: int


@dataclass(frozen=True)
class MapInsightSnapshot:
    """Результат базового инсайта по карте (best/worst)."""

    map_name: str
    winrate: int
    matches: int


@dataclass(frozen=True)
class MapReliableSnapshot:
    """Результат анализа 'надёжной' карты."""

    map_name: str
    winrate: int
    matches: int


@dataclass(frozen=True)
class MapsInsightSnapshot:
    """Полный результат анализа карт игрока."""

    best: MapInsightSnapshot
    worst: MapInsightSnapshot
    reliable: MapReliableSnapshot
