"""Модуль модели данных игрока."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.settings.base import Base

if TYPE_CHECKING:
    from app.core.models.map_stat import MapStat


class Player(Base):
    nickname: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    country: Mapped[str] = mapped_column(nullable=True, index=True)
    verified: Mapped[bool] = mapped_column(default=False, server_default=text("false"))
    steam_nickname: Mapped[str | None] = mapped_column(nullable=True)
    steam_id_64: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    faceit_url: Mapped[str] = mapped_column(nullable=False)
    player_id: Mapped[str] = mapped_column(primary_key=True)
    friends_count: Mapped[int] = mapped_column(default=0, server_default=text("0"))
    activated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    region: Mapped[str] = mapped_column(nullable=False, index=True)
    skill_level: Mapped[int] = mapped_column(nullable=False, index=True)
    faceit_elo: Mapped[int] = mapped_column(nullable=False, index=True)

    map_stats: Mapped[list["MapStat"]] = relationship(
        back_populates="player",
        cascade="all, delete-orphan",
    )
