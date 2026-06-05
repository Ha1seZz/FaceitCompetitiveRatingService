"""Схемы Pydantic для сущности 'Матч'."""

from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.config import settings


class MatchPlayerSchema(BaseModel):
    """Схема данных игрока в конкретном матче."""

    player_id: str
    nickname: str
    membership: str
    game_player_id: int
    game_player_name: str
    game_skill_level: int = 0


class TeamSchema(BaseModel):
    """Схема данных команды внутри матча."""

    faction_id: str
    name: str
    roster: list[MatchPlayerSchema] = Field(alias="players")
    win_probability: float | None = None
    average_skill_level: int | None = None
    rating: int | None = None

    class Config:
        from_attributes = True
        populate_by_name = True


class MatchDetails(BaseModel):
    """Основная схема данных матча."""

    match_id: str
    region: str
    status: str

    competition_id: str
    competition_type: str
    competition_name: str
    organizer_id: str

    teams: list[TeamSchema]

    maps: list[str]
    location: str

    winner: str
    score: dict[str, int]

    configured_at: datetime
    started_at: datetime
    finished_at: datetime

    best_of: int
    calculate_elo: bool
    faceit_url: str


class MatchStats(BaseModel):
    """Дополнительная статистика матча (расширяемая)."""

    pass


class MatchCreate(MatchDetails, MatchStats):
    """Объединенная схема для создания или синхронизации матча в БД."""

    pass


class MatchPublic(MatchStats, MatchDetails):
    """Объединенная схема для вывода матча."""

    model_config = ConfigDict(from_attributes=True)


class MatchShortResponse(BaseModel):
    """Легкая схема для отображения матча в списках (без тяжелых вложенных связей)."""

    match_id: str
    region: str
    status: str
    competition_name: str
    configured_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None
    best_of: int
    winner: str | None = None
    faceit_url: str

    class Config:
        from_attributes = True
