"""Модуль модели статистики игрока."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.settings.base import Base

if TYPE_CHECKING:
    from app.infrastructure.db.models import Player


class PlayerStats(Base):
    __tablename__ = "player_stats"

    player_id: Mapped[str] = mapped_column(
        ForeignKey("players.player_id", ondelete="CASCADE"),
        primary_key=True,
    )
    matches_analyzed: Mapped[int] = mapped_column(nullable=False)
    winrate: Mapped[float] = mapped_column(nullable=False)
    avg_kills: Mapped[float] = mapped_column(nullable=False)
    avg_deaths: Mapped[float] = mapped_column(nullable=False)
    avg_assists: Mapped[float] = mapped_column(nullable=False)
    avg_damage: Mapped[float] = mapped_column(nullable=False)
    kd_ratio: Mapped[float] = mapped_column(nullable=False)
    kr_ratio: Mapped[float] = mapped_column(nullable=False)
    headshots_percent: Mapped[float] = mapped_column(nullable=False)
    adr: Mapped[float] = mapped_column(nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        server_default=func.now(),
        nullable=False,
    )

    player: Mapped["Player"] = relationship(back_populates="stats")
