"""Модуль модели данных игрока."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.settings.base import Base


class Player(Base):
    # Основная информация профиля Faceit
    nickname: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    country: Mapped[str] = mapped_column(nullable=True, index=True)
    verified: Mapped[bool] = mapped_column(default=False, server_default=text("false"))

    # Связь со сторонними сервисами
    steam_nickname: Mapped[str] = mapped_column(nullable=True)
    # Используется BigInteger для корректного хранения длинных 64-битных ID Steam
    steam_id_64: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)

    # Идентификаторы и внешние ссылки
    faceit_url: Mapped[str] = mapped_column(nullable=False)
    player_id: Mapped[str] = mapped_column(primary_key=True)

    # Социальные показатели и метаданные
    friends_count: Mapped[int] = mapped_column(default=0, server_default=text("0"))
    activated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    # Актуальная игровая статистика (Counter-Strike)
    region: Mapped[str] = mapped_column(nullable=False, index=True)
    skill_level: Mapped[int] = mapped_column(nullable=False, index=True)
    faceit_elo: Mapped[int] = mapped_column(nullable=False, index=True)
