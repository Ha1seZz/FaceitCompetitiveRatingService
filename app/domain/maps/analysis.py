from app.domain.maps.models import MapStatSnapshot
from app.schemas.maps_insight import MapsInsight
from app.core.config import settings


def analyze_maps(
    maps_stats: list[MapStatSnapshot],
    min_matches: int = settings.player.min_matches_for_analysis,
) -> MapsInsight | None:
    """Выбирает лучшую и худшую карту по winrate при минимуме матчей min_matches."""
    valid_maps = [m for m in maps_stats if m.matches >= min_matches]

    if not valid_maps:
        return None

    best = max(valid_maps, key=lambda m: (m.winrate, m.matches))
    worst = min(valid_maps, key=lambda m: (m.winrate, -m.matches))

    return {
        "best": {
            "map": best.map_name,
            "winrate": round(best.winrate),
            "matches": best.matches,
        },
        "worst": {
            "map": worst.map_name,
            "winrate": round(worst.winrate),
            "matches": worst.matches,
        },
    }
