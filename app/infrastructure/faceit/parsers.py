"""Парсер для трансформации сырых данных из Faceit API в удобную для модели структуру."""

from datetime import datetime, timezone
from app.core.config import settings


def parse_faceit_match_json(raw_data: dict) -> dict:
    """Адаптер: превращает грязный JSON Faceit в плоский словарь для нашей БД."""
    data = raw_data.copy()

    # Трансформация команд
    raw_teams = data.get("teams", {})
    teams_list = []
    for faction_key in ("faction1", "faction2"):
        t = raw_teams.get(faction_key, {})
        if not t:
            continue

        stats = t.get("stats", {})
        teams_list.append(
            {
                "faction_id": t.get("faction_id"),
                "name": t.get("name"),
                "players": [
                    {
                        "player_id": p.get("player_id"),
                        "nickname": p.get("nickname"),
                        "membership": p.get("membership"),
                        "game_player_id": p.get("game_player_id"),
                        "game_player_name": p.get("game_player_name"),
                        "game_skill_level": p.get("game_skill_level", 0),
                    }
                    for p in t.get("roster", [])
                ],
                "win_probability": stats.get("winProbability"),
                "average_skill_level": stats.get("skillLevel", {}).get("average"),
                "rating": stats.get("rating"),
            }
        )
    data["teams"] = teams_list

    # Конвертация строк в datetime с принудительным UTC
    for field in ["configured_at", "started_at", "finished_at"]:
        value = data.get(field)
        if value in (None, 0):
            data[field] = datetime.now(timezone.utc)
        elif isinstance(value, (int, float)):
            data[field] = datetime.fromtimestamp(value, tz=timezone.utc)

    # Голосование
    voting = data.get("voting", {})
    data["maps"] = voting.get("map", {}).get("pick", [])
    loc_picks = voting.get("location", {}).get("pick", [])
    data["location"] = loc_picks[0] if loc_picks else "unknown"

    # Результаты
    results = data.get("results", {})
    data["winner"] = results.get("winner", "TBD")
    data["score"] = results.get("score", {})

    # Формирование локализованной ссылки
    url: str = data.get("faceit_url", "")
    data["faceit_url"] = url.replace("{lang}", settings.faceit.default_language)

    return data
