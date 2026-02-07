from app.domain.maps.models import MapStatSnapshot


MIN_MATCHES = 10


def analyze_maps(maps_stats: list[MapStatSnapshot]) -> dict | None:
    """Выбирает лучшую и худшую карту по winrate при минимуме матчей MIN_MATCHES."""
    valid_maps = [m for m in maps_stats if m.matches >= MIN_MATCHES]

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
