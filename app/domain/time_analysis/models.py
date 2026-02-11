"""Доменные snapshot-структуры для анализа "когда лучше играть"."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class MatchTimeSnapshot:
    """Снимок одного матча для анализа по времени."""

    finished_at_utc: datetime
    is_win: bool | None


@dataclass(frozen=True)
class TimeWindowSnapshot:
    """Агрегированная статистика по одному временному окну."""

    start_hour: int
    window_size_hours: int
    matches: int
    wins: int
    winrate_percent: int


@dataclass(frozen=True)
class WhenToPlaySnapshot:
    """Результат доменного анализа: лучшее окно по выбранной метрике."""

    best_window: TimeWindowSnapshot
