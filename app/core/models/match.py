from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, JSON, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.settings.base import Base


class Match(Base):
    __tablename__ = "matches"
    match_id: Mapped[str] = mapped_column(primary_key=True)
    region: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False)

    # Информация о соревновании
    competition_id: Mapped[str] = mapped_column(nullable=False)
    competition_type: Mapped[str] = mapped_column(nullable=False)
    competition_name: Mapped[str] = mapped_column(nullable=False)
    organizer_id: Mapped[str] = mapped_column(nullable=False)

    # Команды
    teams: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    # Голосование
    map: Mapped[str] = mapped_column(nullable=False)
    location: Mapped[str] = mapped_column(nullable=False)

    # Результат
    winner: Mapped[str] = mapped_column(nullable=False)
    score: Mapped[dict[str, int]] = mapped_column(JSON, nullable=False)

    # Временные метки
    configured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Дополнительные данные
    best_of: Mapped[int] = mapped_column(nullable=False)
    calculate_elo: Mapped[bool] = mapped_column(default=True, server_default=text("true"))
    faceit_url: Mapped[str] = mapped_column(nullable=False)
