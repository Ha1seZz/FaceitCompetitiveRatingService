"""Модуль модели данных команды конкретного матча."""

from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.models.mixins.id_int_pk import IdIntPkMixin
from app.core.settings.base import Base

if TYPE_CHECKING:
    from app.infrastructure.db.models import Match
    from app.infrastructure.db.models import MatchPlayer


class Team(IdIntPkMixin, Base):
    match_id: Mapped[str] = mapped_column(
        ForeignKey("matches.match_id", ondelete="CASCADE"),
        nullable=False,
    )

    faction_id: Mapped[str] = mapped_column(nullable=False, index=True)
    name: Mapped[str] = mapped_column(nullable=False)

    win_probability: Mapped[float] = mapped_column(nullable=True)
    average_skill_level: Mapped[int] = mapped_column(nullable=True)
    rating: Mapped[int] = mapped_column(nullable=True)

    players: Mapped[list["MatchPlayer"]] = relationship(
        "MatchPlayer",
        back_populates="team",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    # Обратная связь с матчем
    match: Mapped["Match"] = relationship("Match", back_populates="teams")
