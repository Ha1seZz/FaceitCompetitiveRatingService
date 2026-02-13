"""Сервис кэширования истории матчей игрока."""

from datetime import datetime, timezone

import httpx

from app.schemas import MatchHistoryRow
from app.domain.time_analysis.analysis import build_time_snapshot
from app.infrastructure.db.repositories import MatchHistoryRepository, PlayerRepository
from app.infrastructure.faceit.client import FaceitClient
from app.core.exceptions import ExternalServiceUnavailable
from app.core.config import settings


class MatchHistoryService:
    """Application-сервис: загрузка/кэширование истории матчей игрока для аналитики."""

    def __init__(
        self,
        match_history_repo: MatchHistoryRepository,
        player_repo: PlayerRepository,
        faceit_client: FaceitClient,
    ):
        self.match_history_repo = match_history_repo
        self.player_repo = player_repo
        self.faceit_client = faceit_client

    async def get_or_fetch_match_history(self, player_id: str) -> list[MatchHistoryRow]:
        """Возвращает историю матчей игрока."""
        updated_at = await self.player_repo.get_match_history_updated_at(player_id)

        if not self._is_cache_stale(updated_at):
            return await self.match_history_repo.get_last(
                player_id=player_id,
                limit=settings.match_history.limit,
            )
        try:
            raw_matches = await self.faceit_client.get_player_match_history(
                player_id,
                max_matches=settings.match_history.limit,
            )
        except(ExternalServiceUnavailable, httpx.HTTPError):
           # Фолбэк: возвращаем последнее сохранённое, даже если кэш старый
            return await self.match_history_repo.get_last(
                player_id=player_id,
                limit=settings.match_history.limit,
            )

        rows: list[MatchHistoryRow] = []

        for match in raw_matches:
            try:
                match_id = match.get("match_id")
                if not match_id:
                    continue

                snapshot = build_time_snapshot(match, player_id)

                # В БД храним только матчи с известным исходом (is_win: bool).
                if snapshot.is_win is None:
                    continue

                rows.append(
                    MatchHistoryRow(
                        match_id=match_id,
                        finished_at_utc=snapshot.finished_at_utc,
                        is_win=snapshot.is_win,
                    )
                )
            except ValueError:
                # Некорректные/неполные данные матча (например, нет finished_at)
                continue

        await self.match_history_repo.replace(player_id=player_id, rows=rows)
        await self.player_repo.set_match_history_updated_at(
            player_id,
            datetime.now(timezone.utc),
        )
        return rows

    def _is_cache_stale(self, updated_at: datetime | None) -> bool:
        """True, если кэш отсутствует или старше TTL."""
        if not updated_at:
            return True

        age = datetime.now(timezone.utc) - updated_at
        return age > settings.match_history.ttl
