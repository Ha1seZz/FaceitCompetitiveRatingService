"""
Пакет моделей базы данных.

Экспортирует базовый класс и все доменные модели (Player, Match) для 
централизованного доступа из других частей приложения.
"""

__all__ = (
    "Base",
    "Player",
    "Match",
)

from app.core.settings.base import Base
from .player import Player
from .match import Match
