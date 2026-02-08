from app.schemas import MapInsightItem, MapsInsight
from app.domain.maps.models import MapStatSnapshot

from app.core.exceptions import InsufficientDataError
from app.core.config import settings


def analyze_maps(
    maps_stats: list[MapStatSnapshot],
    min_matches: int = settings.player.min_matches_for_analysis,
) -> MapsInsight | None:
    """Выбирает лучшую и худшую карту по winrate при минимуме матчей min_matches."""
    valid_maps = [m for m in maps_stats if m.matches >= min_matches]

    if not valid_maps:
        raise InsufficientDataError(
            f"Not enough matches for analysis. Minimum {min_matches} matches required."
        )

    best = max(valid_maps, key=lambda m: (m.winrate, m.matches))
    worst = min(valid_maps, key=lambda m: (m.winrate, -m.matches))

    return MapsInsight(
        best=MapInsightItem(
            map=best.map_name,
            winrate=round(best.winrate),
            matches=best.matches,
        ),
        worst=MapInsightItem(
            map=worst.map_name,
            winrate=round(worst.winrate),
            matches=worst.matches,
        ),
    )
