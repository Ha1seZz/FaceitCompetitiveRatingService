"""Use-case: анализ "когда лучше играть" по истории матчей игрока."""

from app.domain.time_analysis.analysis import analyze_play_time, build_time_snapshot
from app.infrastructure.faceit.client import FaceitClient
from app.application.player_service import PlayerService
from app.schemas import WhenToPlayInsight


class TimeAnalysisService:
    """Application сервис для вычисления оптимального времени игры."""

    def __init__(
        self,
        player_service: PlayerService,
        faceit_client: FaceitClient,
    ):
        self.player_service = player_service
        self.faceit_client = faceit_client

    async def analyze(self, nickname) -> WhenToPlayInsight:
        """Выполняет анализ и возвращает рекомендованное временное окно игры."""
        player = await self.player_service.get_or_create_player(nickname=nickname)
        matches = await self.faceit_client.get_player_match_history(player.player_id)

        snapshots = []
        skipped_invalid = 0

        for match in matches:
            try:
                snapshots.append(build_time_snapshot(match, player.player_id))
            except ValueError:
                # Пропускаем матчи без finished_at или с некорректными полями времени
                skipped_invalid += 1

        insight = analyze_play_time(snapshots).best_window

        return WhenToPlayInsight(
            start_hour=insight.start_hour,
            end_hour=(insight.start_hour + insight.window_size_hours) % 24,
            matches=insight.matches,
            wins=insight.wins,
            winrate=insight.winrate_percent,
        )
