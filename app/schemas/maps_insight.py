"""DTO-модели для аналитического ответа по картам игрока."""

from pydantic import BaseModel


class MapInsightItem(BaseModel):
    """Элемент краткого инсайта по карте."""

    map: str
    winrate: int
    matches: int


class MapReliableInsight(BaseModel):
    """DTO 'надёжной' карты игрока."""

    map: str
    winrate: int
    matches: int


class MapsInsight(BaseModel):
    """DTO ответа анализа карт игрока."""

    best: MapInsightItem
    worst: MapInsightItem
    reliable: MapReliableInsight
