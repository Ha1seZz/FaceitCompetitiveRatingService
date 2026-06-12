"""Доменные snapshot-структуры для анализа данных игрока."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PlayerDomainModel:
    """Полная доменная модель данных игрока."""

    nickname: str
    verified: bool
    faceit_url: str
    player_id: str
    friends_count: int
    activated_at: datetime
    skill_level: int
    faceit_elo: int
    region: str
    country: str | None = None
    steam_nickname: str | None = None
    steam_id_64: int | None = None
    updated_at: datetime | None = None
    match_history_updated_at: datetime | None = None
