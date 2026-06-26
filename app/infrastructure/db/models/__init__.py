"""
Пакет моделей базы данных.

Экспортирует базовый класс и все доменные модели (Player, Match) для
централизованного доступа из других частей приложения.
"""

__all__ = (
    "Base",
    "MapStat",
    "MatchPlayer",
    "Match",
    "PlayerMatchHistory",
    "PlayerStats",
    "Player",
    "Team",
)

from app.core.settings.base import Base
from .map_stat import MapStat
from .match_player import MatchPlayer
from .match import Match
from .player_match_history import PlayerMatchHistory
from .player_stats import PlayerStats
from .player import Player
from .team import Team
