"""Модуль модели данных команды конкретного матча."""

from typing import TYPE_CHECKING, Any
from sqlalchemy import ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models.mixins.id_int_pk import IdIntPkMixin
from app.core.settings.base import Base

if TYPE_CHECKING:
    from app.core.models.match import Match
    

class Team(IdIntPkMixin, Base):
    """Модель участника матча. Хранит состав и статистику на момент игры."""
    match_id: Mapped[str] = mapped_column(
        ForeignKey("matches.match_id", ondelete="CASCADE")
    )

    faction_id: Mapped[str] = mapped_column(nullable=False, index=True)
    name: Mapped[str] = mapped_column(nullable=False)
    roster: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False)

    win_probability: Mapped[float] = mapped_column(nullable=True)
    average_skill_level: Mapped[int] = mapped_column(nullable=True)
    rating: Mapped[int] = mapped_column(nullable=True)

    # Обратная связь с матчем
    match: Mapped["Match"] = relationship("Match", back_populates="teams")
