from datetime import datetime

from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column

from .mixins.id_int_pk import IdIntPkMixin
from app.core.settings.base import Base


class Player(IdIntPkMixin, Base):
    nickname: Mapped[str] = mapped_column(nullable=False)
    country: Mapped[str] = mapped_column(nullable=True)
    verified: Mapped[bool] = mapped_column(server_default=text("false"))
    steam_nickname: Mapped[str] = mapped_column(nullable=True)
    steam_id_64: Mapped[int] = mapped_column(nullable=False)
    faceit_url: Mapped[str] = mapped_column(nullable=False)
    player_id: Mapped[str] = mapped_column(nullable=False, unique=True)
    friends_count: Mapped[int] = mapped_column(server_default=text("0"))
    activated_at: Mapped[datetime] = mapped_column(nullable=False)

    # Статистика CS
    region: Mapped[str] = mapped_column(nullable=False)
    skill_level: Mapped[int] = mapped_column(nullable=False)
    faceit_elo: Mapped[int] = mapped_column(nullable=False)
