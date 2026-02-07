"""Доменные модели для анализа статистики по картам."""

from dataclasses import dataclass


@dataclass
class MapStatSnapshot:
    map_name: str
    winrate: float
    matches: int
