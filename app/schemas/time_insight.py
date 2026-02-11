"""DTO-модели для ответа эндпоинта /when-to-play."""

from pydantic import BaseModel


class WhenToPlayInsight(BaseModel):
    """Результат анализа "когда лучше играть" (временное окно по UTC)."""

    start_hour: int
    end_hour: int
    matches: int
    wins: int
    winrate: float
