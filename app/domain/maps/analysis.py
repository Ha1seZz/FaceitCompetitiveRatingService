"""Чистая бизнес-логика анализа карт игрока."""

from math import log10

from .models import (
    MapReliableSnapshot,
    MapStatSnapshot,
    MapInsightSnapshot,
    MapsInsightSnapshot,
)
from app.core.exceptions import InsufficientDataError


def analyze_maps(
    maps_stats: list[MapStatSnapshot],
    min_matches: int,
) -> MapsInsightSnapshot | None:
    """
    Определяет:
    - Лучшую карту (макс winrate)
    - Худшую карту (мин winrate)
    - Надёжную карту (winrate + стабильность выборки)
    """
    valid_maps = [m for m in maps_stats if m.matches >= min_matches]

    if not valid_maps:
        raise InsufficientDataError(
            f"Not enough matches for analysis. Minimum {min_matches} matches required."
        )

    best = max(valid_maps, key=lambda m: (m.winrate, m.matches))
    worst = min(valid_maps, key=lambda m: (m.winrate, -m.matches))
    reliable = _find_reliable_map(valid_maps)

    return MapsInsightSnapshot(
        best=MapInsightSnapshot(best.map_name, round(best.winrate), best.matches),
        worst=MapInsightSnapshot(worst.map_name, round(worst.winrate), worst.matches),
        reliable=reliable,
    )


def _find_reliable_map(
    valid_maps: list[MapStatSnapshot],
) -> MapReliableSnapshot:
    """
    Находит карту, где игрок стабильно хорош.
    Формула: winrate * log10(matches + 1)
    """

    def score(m: MapStatSnapshot) -> float:
        return m.winrate * log10(m.matches + 1)

    reliable = max(valid_maps, key=score)

    return MapReliableSnapshot(
        map_name=reliable.map_name,
        winrate=round(reliable.winrate),
        matches=reliable.matches,
    )
