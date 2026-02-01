"""Модуль модели данных матча."""

from datetime import datetime
from typing import Any

from sqlalchemy import ARRAY, DateTime, JSON, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.settings.base import Base


class Match(Base):
    __tablename__ = "matches"

    # Основные идентификаторы
    match_id: Mapped[str] = mapped_column(primary_key=True)
    region: Mapped[str] = mapped_column(nullable=False, index=True)
    status: Mapped[str] = mapped_column(nullable=False, index=True)

    # Информация о соревновании (турнир, лига или хаб)
    competition_id: Mapped[str] = mapped_column(nullable=False, index=True)
    competition_type: Mapped[str] = mapped_column(nullable=False, index=True)
    competition_name: Mapped[str] = mapped_column(nullable=False)
    organizer_id: Mapped[str] = mapped_column(nullable=False, index=True)

    # Данные о командах (хранятся в JSON для гибкости структуры участников)
    teams: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    # Итоги голосования капитанов
    maps: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        server_default="{}",
        index=True,
    )
    location: Mapped[str] = mapped_column(nullable=False)

    # Итоговый результат
    winner: Mapped[str] = mapped_column(nullable=False)
    score: Mapped[dict[str, int]] = mapped_column(JSON, nullable=False)

    # Временные метки в формате UTC с поддержкой часовых поясов
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

    # Параметры матча и внешние ссылки
    best_of: Mapped[int] = mapped_column(nullable=False)
    calculate_elo: Mapped[bool] = mapped_column(
        default=True,
        server_default=text("true"),
        index=True,
    )
    faceit_url: Mapped[str] = mapped_column(nullable=False)
