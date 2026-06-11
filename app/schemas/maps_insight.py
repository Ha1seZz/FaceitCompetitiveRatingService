"""DTO-модели для аналитического ответа по картам игрока."""

from pydantic import BaseModel, ConfigDict


class MapInsightItem(BaseModel):
    """Элемент краткого инсайта по карте."""

    map_name: str
    winrate: int
    matches: int


class MapReliableInsight(BaseModel):
    """DTO 'надёжной' карты игрока."""

    map_name: str
    winrate: int
    matches: int


class MapsInsight(BaseModel):
    """DTO ответа анализа карт игрока."""

    model_config = ConfigDict(from_attributes=True)

    best: MapInsightItem
    worst: MapInsightItem
    reliable: MapReliableInsight
