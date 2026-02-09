"""Доменные структуры (snapshots) для анализа статистики игрока по картам."""

from dataclasses import dataclass


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
