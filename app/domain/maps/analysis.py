"""Чистая бизнес-логика анализа карт игрока."""

from .models import MapStatSnapshot, MapInsightSnapshot, MapsInsightSnapshot

from app.core.exceptions import InsufficientDataError
from app.core.config import settings


def analyze_maps(
    maps_stats: list[MapStatSnapshot],
    min_matches: int = settings.player.min_matches_for_analysis,
) -> MapsInsightSnapshot | None:
    """Определяет лучшую и худшую карту игрока на основе winrate при минимуме матчей min_matches."""
    valid_maps = [m for m in maps_stats if m.matches >= min_matches]

    if not valid_maps:
        raise InsufficientDataError(
            f"Not enough matches for analysis. Minimum {min_matches} matches required."
        )

    best = max(valid_maps, key=lambda m: (m.winrate, m.matches))
    worst = min(valid_maps, key=lambda m: (m.winrate, -m.matches))

    return MapsInsightSnapshot(
        best=MapInsightSnapshot(
            map_name=best.map_name,
            winrate=round(best.winrate),
            matches=best.matches,
        ),
        worst=MapInsightSnapshot(
            map_name=worst.map_name,
            winrate=round(worst.winrate),
            matches=worst.matches,
        ),
    )
