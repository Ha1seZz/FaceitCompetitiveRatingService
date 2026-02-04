"""Модуль модели данных статистики игрока по картам."""

from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models.mixins.id_int_pk import IdIntPkMixin
from app.core.settings.base import Base

if TYPE_CHECKING:
    from app.core.models.player import Player


class MapStat(IdIntPkMixin, Base):
    __tablename__ = "map_stats"
    __table_args__ = (
        UniqueConstraint(
            "player_id",
            "map_name",
            name="uq_player_map_stats",
        ),
    )

    map_name: Mapped[str] = mapped_column(nullable=False)
    matches: Mapped[int] = mapped_column(nullable=False, default=0)
    won: Mapped[int] = mapped_column(nullable=False, default=0)
    lost: Mapped[int] = mapped_column(nullable=False, default=0)
    winrate: Mapped[float] = mapped_column(nullable=False, default=0.0)
    average_kills: Mapped[float] = mapped_column(nullable=False, default=0.0)
    average_deaths: Mapped[float] = mapped_column(nullable=False, default=0.0)
    average_kd_ratio: Mapped[float] = mapped_column(nullable=False, default=0.0)
    average_kr_ratio: Mapped[float] = mapped_column(nullable=False, default=0.0)
    hs: Mapped[float] = mapped_column(nullable=False, default=0.0)
    adr: Mapped[float] = mapped_column(nullable=False, default=0.0)
    rounds: Mapped[int] = mapped_column(nullable=False, default=0)
    kills: Mapped[int] = mapped_column(nullable=False, default=0)
    assists: Mapped[int] = mapped_column(nullable=False, default=0)
    deaths: Mapped[int] = mapped_column(nullable=False, default=0)
    headshots: Mapped[int] = mapped_column(nullable=False, default=0)
    total_damage: Mapped[int] = mapped_column(nullable=False, default=0)
    penta_kills: Mapped[int] = mapped_column(nullable=False, default=0)

    player_id: Mapped[str] = mapped_column(
        ForeignKey("players.player_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    player: Mapped["Player"] = relationship(back_populates="map_stats")

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        server_default=func.now(),
    )
