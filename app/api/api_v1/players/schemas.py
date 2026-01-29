from datetime import datetime
from typing import Any
from pydantic import BaseModel, model_validator


class PlayerProfileDetails(BaseModel):
    nickname: str
    country: str
    verified: bool
    steam_nickname: str
    steam_id_64: int
    faceit_url: str
    player_id: str
    friends_count: int
    activated_at: datetime

    @model_validator(mode="before")
    @classmethod
    def prepare_profile(cls, data: Any) -> Any:
        if isinstance(data, dict):
            data["friends_count"] = len(data["friends_ids"])

            # Формирует рабочую ссылку, заменяя плейсхолдер на русский язык
            url: str = data.get("faceit_url", "")
            data["faceit_url"] = url.replace("{lang}", "ru")
        return data


class PlayerCSStats(BaseModel):
    region: str
    skill_level: int
    faceit_elo: int

    @model_validator(mode="before")
    @classmethod
    def extract_cs_stats(cls, data: Any) -> Any:
        if isinstance(data, dict):
            games: dict = data.get("games", {})
            cs_info = games.get("cs2") or games.get("csgo") or {}

            data["region"] = cs_info.get("region", "")
            data["skill_level"] = cs_info.get("skill_level", 0)
            data["faceit_elo"] = cs_info.get("faceit_elo", 0)

        return data


class PlayerCreate(PlayerProfileDetails, PlayerCSStats):
    pass
