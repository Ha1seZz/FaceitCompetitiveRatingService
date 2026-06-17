"""Use-case: анализ "когда лучше играть" по истории матчей игрока."""

from typing import Callable

from app.domain.time_analysis.models import MatchTimeSnapshot, TimeWindowSnapshot
from app.domain.time_analysis.analysis import analyze_play_time
from app.application.match_history_service import MatchHistoryService
from app.application.player_service import PlayerService


class TimeAnalysisService:
    """Application сервис для вычисления оптимального времени игры."""

    def __init__(
        self,
        player_service: PlayerService,
        match_history_service: MatchHistoryService,
    ):
        self.player_service = player_service
        self.match_history_service = match_history_service

    async def analyze(
        self,
        nickname: str,
        enqueue_background_task: Callable[..., None] | None = None,
    ) -> TimeWindowSnapshot:
        """Возвращает рекомендацию 'когда лучше играть' по истории матчей (окно в UTC)."""
        player = await self.player_service.get_or_create_player(nickname=nickname)

        rows = await self.match_history_service.get_or_fetch_match_history(
            player_id=player.player_id,
            updated_at=player.match_history_updated_at,
            enqueue_background_task=enqueue_background_task,
        )

        snapshots = [
            MatchTimeSnapshot(
                finished_at_utc=row.finished_at_utc,
                is_win=row.is_win,
            )
            for row in rows
        ]

        return analyze_play_time(snapshots)
