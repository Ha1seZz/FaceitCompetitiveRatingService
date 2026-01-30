from datetime import datetime

from sqlalchemy import BigInteger, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.settings.base import Base


class Player(Base):
    """Модель игрока Faceit."""
    # Faceit профиль
    nickname: Mapped[str] = mapped_column(unique=True, nullable=False)
    country: Mapped[str] = mapped_column(nullable=True)
    verified: Mapped[bool] = mapped_column(default=False, server_default=text("false"))
    steam_nickname: Mapped[str] = mapped_column(nullable=True)
    steam_id_64: Mapped[int] = mapped_column(BigInteger, nullable=False)
    faceit_url: Mapped[str] = mapped_column(nullable=False)
    player_id: Mapped[str] = mapped_column(primary_key=True)
    friends_count: Mapped[int] = mapped_column(default=0, server_default=text("0"))
    activated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Статистика CS
    region: Mapped[str] = mapped_column(nullable=False)
    skill_level: Mapped[int] = mapped_column(nullable=False)
    faceit_elo: Mapped[int] = mapped_column(nullable=False)
