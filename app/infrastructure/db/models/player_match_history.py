"""Модель хранения истории матчей игрока для аналитики времени игры."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.settings.base import Base

if TYPE_CHECKING:
    from app.infrastructure.db.models import Player


class PlayerMatchHistory(Base):
    __tablename__ = "player_match_history"
    __table_args__ = (
        Index("ix_player_match_history_player_time", "player_id", "finished_at_utc"),
    )

    player_id: Mapped[str] = mapped_column(
        ForeignKey("players.player_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    match_id: Mapped[str] = mapped_column(
        nullable=False,
        primary_key=True,
    )

    finished_at_utc: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    is_win: Mapped[bool] = mapped_column(nullable=False)

    player: Mapped["Player"] = relationship(back_populates="match_history")
