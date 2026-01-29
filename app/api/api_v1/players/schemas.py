from typing import Any
from pydantic import BaseModel, model_validator


class PlayerProfileDetails(BaseModel):
    country: str
    nickname: str
    faceit_url: str
    player_id: str

    @model_validator(mode="before")
    @classmethod
    def prepare_profile(cls, data: Any) -> Any:
        if isinstance(data, dict):
            url: str = data.get("faceit_url", "")
            data["faceit_url"] = url.replace("{lang}", "ru")
        return data


class PlayerCSStats(BaseModel):
    region: str
    skill_level: int
    faceit_elo: int
    game_player_name: str
    game_player_id: int

    @model_validator(mode="before")
    @classmethod
    def extract_cs_stats(cls, data: Any) -> Any:
        if isinstance(data, dict):
            games: dict = data.get("games", {})
            cs_info = games.get("cs2") or games.get("csgo") or {}

            data["region"] = cs_info.get("region", "")
            data["skill_level"] = cs_info.get("skill_level", 0)
            data["faceit_elo"] = cs_info.get("faceit_elo", 0)
            data["game_player_name"] = cs_info.get("game_player_name", "")
            data["game_player_id"] = cs_info.get("game_player_id", 0)

        return data
