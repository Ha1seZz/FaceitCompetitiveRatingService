"""Модуль модели данных игрока команды конкретного матча."""

from typing import TYPE_CHECKING
from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.models.mixins.id_int_pk import IdIntPkMixin
from app.core.settings.base import Base

if TYPE_CHECKING:
    from app.infrastructure.db.models import Team


class MatchPlayer(IdIntPkMixin, Base):
    __tablename__ = "match_players"

    team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
    )

    player_id: Mapped[str] = mapped_column(index=True)
    nickname: Mapped[str] = mapped_column(nullable=False)
    membership: Mapped[str] = mapped_column(index=True)
    game_player_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    game_player_name: Mapped[str | None] = mapped_column(nullable=True)
    game_skill_level: Mapped[int] = mapped_column(default=0, server_default="0")

    # Обратная связь с командой
    team: Mapped["Team"] = relationship("Team", back_populates="players")
