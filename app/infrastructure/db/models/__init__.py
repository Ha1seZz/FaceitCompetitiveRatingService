"""
Пакет моделей базы данных.

Экспортирует базовый класс и все доменные модели (Player, Match) для
централизованного доступа из других частей приложения.
"""

__all__ = (
    "Base",
    "Player",
    "Match",
    "Team",
    "MatchPlayer",
    "MapStat",
    "PlayerMatchHistory",
)

from app.core.settings.base import Base
from .player import Player
from .match import Match
from .team import Team
from .match_player import MatchPlayer
from .map_stat import MapStat
from .player_match_history import PlayerMatchHistory
