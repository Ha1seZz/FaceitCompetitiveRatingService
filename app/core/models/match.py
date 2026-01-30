from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.settings.base import Base


class Match(Base):
    match_id: Mapped[str] = mapped_column(primary_key=True)
    region: Mapped[str] = mapped_column(nullable=False)
    competition_type: Mapped[str] = mapped_column(nullable=False)
    competition_name: Mapped[str] = mapped_column(nullable=False)
    organizer_id: Mapped[str] = mapped_column(nullable=False)
    teams: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    configured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    best_of: Mapped[int] = mapped_column(nullable=False)
    results: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(nullable=False)
    faceit_url: Mapped[str] = mapped_column(nullable=False)
