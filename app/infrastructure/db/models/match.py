"""Модуль модели данных матча."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ARRAY, DateTime, JSON, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.settings.base import Base

if TYPE_CHECKING:
    from app.infrastructure.db.models import Team


class Match(Base):
    __tablename__ = "matches"

    match_id: Mapped[str] = mapped_column(primary_key=True)
    region: Mapped[str] = mapped_column(nullable=False, index=True)
    status: Mapped[str] = mapped_column(nullable=False, index=True)

    competition_id: Mapped[str] = mapped_column(nullable=False, index=True)
    competition_type: Mapped[str] = mapped_column(nullable=False, index=True)
    competition_name: Mapped[str] = mapped_column(nullable=False)
    organizer_id: Mapped[str] = mapped_column(nullable=False, index=True)

    teams: Mapped[list["Team"]] = relationship(
        "Team",
        back_populates="match",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    maps: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        server_default="{}",
    )
    location: Mapped[str] = mapped_column(nullable=False)

    winner: Mapped[str] = mapped_column(nullable=False)
    score: Mapped[dict[str, int]] = mapped_column(JSON, nullable=False)

    configured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    finished_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    best_of: Mapped[int] = mapped_column(nullable=False)
    calculate_elo: Mapped[bool] = mapped_column(
        default=True,
        server_default=text("true"),
        index=True,
    )
    faceit_url: Mapped[str] = mapped_column(nullable=False)
