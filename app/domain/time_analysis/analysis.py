"""Чистая доменная логика анализа "когда лучше играть"."""

from typing import Any
from collections import defaultdict
from datetime import datetime, timezone

from .models import MatchTimeSnapshot, TimeWindowSnapshot, WhenToPlaySnapshot
from app.core.exceptions import InsufficientDataError


def find_player_faction(match: dict[str, Any], player_id: str) -> str:
    """Определяет, в какой фракции (faction1/faction2) находится игрок в конкретном матче."""
    teams: dict = match.get("teams", {})

    for faction_key in ("faction1", "faction2"):
        faction = teams.get(faction_key) or {}
        players = faction.get("players") or []

        if any(p.get("player_id") == player_id for p in players):
            return faction_key

    raise ValueError(f"Player {player_id} not found in match teams")


def compute_match_result(match: dict[str, Any], player_id: str) -> bool | None:
    """Вычисляет победу игрока в матче."""
    winner_faction = (match.get("results") or {}).get("winner")  # 'faction1'|'faction2'
    if winner_faction not in ("faction1", "faction2"):
        return None

    try:
        player_faction = find_player_faction(match, player_id)
    except ValueError:
        return None

    return player_faction == winner_faction


def build_time_snapshot(match: dict[str, Any], player_id: str) -> MatchTimeSnapshot:
    """Преобразует сырой матч Faceit в MatchTimeSnapshot."""
    finished_at_ts = match.get("finished_at")
    if not isinstance(finished_at_ts, int):
        raise ValueError("Match has no valid finished_at timestamp")

    finished_at_utc = datetime.fromtimestamp(finished_at_ts, tz=timezone.utc)
    is_win = compute_match_result(match, player_id)

    return MatchTimeSnapshot(finished_at_utc=finished_at_utc, is_win=is_win)


def analyze_play_time(
    snapshots: list[MatchTimeSnapshot],
    window_size_hours: int = 3,
    min_matches_in_window: int = 30,
    min_valid_matches_in_window: int = 20,
) -> WhenToPlaySnapshot:
    """Находит лучшее окно по времени суток для игры."""
    if window_size_hours <= 0 or window_size_hours > 24:
        raise ValueError("window_size_hours must be in range 1..24")

    matches_by_hour = defaultdict(int)        # Все матчи (включая is_win=None)
    valid_matches_by_hour = defaultdict(int)  # Матчи с известным исходом
    wins_by_hour = defaultdict(int)           # Победы среди матчей с известным исходом

    for snapshot in snapshots:
        hour = snapshot.finished_at_utc.hour
        matches_by_hour[hour] += 1

        if snapshot.is_win is None:
            continue

        valid_matches_by_hour[hour] += 1
        wins_by_hour[hour] += int(snapshot.is_win)

    candidates: list[TimeWindowSnapshot] = []

    for start_hour in range(24):
        window_hours = [(start_hour + i) % 24 for i in range(window_size_hours)]

        total_matches_in_window = sum(matches_by_hour[h] for h in window_hours)
        if total_matches_in_window < min_matches_in_window:
            continue

        valid_matches_in_window = sum(valid_matches_by_hour[h] for h in window_hours)
        if valid_matches_in_window < min_valid_matches_in_window:
            continue

        wins_in_window = sum(wins_by_hour[h] for h in window_hours)
        winrate_percent = round((wins_in_window / valid_matches_in_window) * 100)

        candidates.append(
            TimeWindowSnapshot(
                start_hour=start_hour,
                window_size_hours=window_size_hours,
                matches=valid_matches_in_window,
                wins=wins_in_window,
                winrate_percent=winrate_percent,
            )
        )

    if not candidates:
        raise InsufficientDataError(
            "Not enough data for time-window analysis. "
            f"Need >= {min_matches_in_window} total matches per {window_size_hours}h window "
            f"and >= {min_valid_matches_in_window} matches with known outcome."
        )

    best = max(candidates, key=lambda w: (w.winrate_percent, w.matches))
    return WhenToPlaySnapshot(best_window=best)
