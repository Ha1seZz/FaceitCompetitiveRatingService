"""Pydantic-схемы для кэша истории матчей игрока."""

from datetime import datetime

from pydantic import BaseModel


class MatchHistoryRow(BaseModel):
    """Одна строка истории матчей игрока (минимум данных для аналитики/кэша)."""

    match_id: str
    finished_at_utc: datetime
    is_win: bool
