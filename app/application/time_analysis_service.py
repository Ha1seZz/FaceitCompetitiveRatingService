"""Use-case: анализ "когда лучше играть" по истории матчей игрока."""

from app.domain.time_analysis.models import MatchTimeSnapshot
from app.domain.time_analysis.analysis import analyze_play_time
from app.application.match_history_service import MatchHistoryService
from app.application.player_service import PlayerService
from app.schemas import WhenToPlayInsight


class TimeAnalysisService:
    """Application сервис для вычисления оптимального времени игры."""

    def __init__(
        self,
        player_service: PlayerService,
        match_history_service: MatchHistoryService,
    ):
        self.player_service = player_service
        self.match_history_service = match_history_service

    async def analyze(self, nickname) -> WhenToPlayInsight:
        """Возвращает рекомендацию 'когда лучше играть' по истории матчей (окно в UTC)."""
        player = await self.player_service.get_or_create_player(nickname=nickname)
        rows = await self.match_history_service.get_or_fetch_match_history(
            player.player_id
        )

        snapshots = [
            MatchTimeSnapshot(
                finished_at_utc=row.finished_at_utc,
                is_win=row.is_win,
            )
            for row in rows
        ]

        insight = analyze_play_time(snapshots).best_window

        return WhenToPlayInsight(
            start_hour=insight.start_hour,
            end_hour=(insight.start_hour + insight.window_size_hours) % 24,
            matches=insight.matches,
            wins=insight.wins,
            winrate=insight.winrate_percent,
        )
