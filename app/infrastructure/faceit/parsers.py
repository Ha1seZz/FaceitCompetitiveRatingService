"""Парсер для трансформации сырых данных из Faceit API в удобную для модели структуру."""

from datetime import datetime, timezone
from typing import Any

from app.core.config import settings


def parse_faceit_match_details(raw_data: dict) -> dict:
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


def parse_faceit_map_stats(data: dict) -> dict[str, Any]:
    """Парсинг игровой статистики по конкретной карте из сырых данных Faceit."""
    s: dict = data.get("stats", {})
    m = int(s.get("Matches", 0))
    w = int(s.get("Wins", 0))
    k = int(s.get("Kills", 0))
    hs = int(s.get("Headshots", 0))

    lost = m - w
    winrate = round(((w / m) * 100), 2) if m > 0 else 0.0
    hs_ratio = round(((hs / k) * 100), 2) if k > 0 else 0.0

    return {
        "map_name": data.get("label"),
        "matches": m,
        "won": w,
        "lost": lost,
        "winrate": winrate,
        "average_kills": float(s.get("Average Kills", 0)),
        "average_deaths": float(s.get("Average Deaths", 0)),
        "average_kd_ratio": float(s.get("Average K/D Ratio", 0)),
        "average_kr_ratio": float(s.get("Average K/R Ratio", 0)),
        "hs": hs_ratio,
        "adr": float(s.get("ADR", 0)),
        "rounds": int(s.get("Rounds", 0)),
        "kills": k,
        "assists": int(s.get("Assists", 0)),
        "deaths": int(s.get("Deaths", 0)),
        "headshots": hs,
        "total_damage": int(s.get("Total Damage", 0)),
        "penta_kills": int(s.get("Penta Kills", 0)),
    }
