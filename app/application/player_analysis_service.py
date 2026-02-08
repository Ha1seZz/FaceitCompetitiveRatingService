"""Use-case анализа игрока."""

from app.schemas.maps_insight import MapInsightItem, MapsInsight
from app.application.maps_stats_service import MapsStatsService
from app.application.player_service import PlayerService
from app.domain.maps.models import MapStatSnapshot
from app.domain.maps.analysis import analyze_maps


class PlayerAnalysisService:
    """Use case: анализ игрока."""

    def __init__(
        self,
        maps_service: MapsStatsService,
        player_service: PlayerService,
    ):
        self.maps_service = maps_service
        self.player_service = player_service

    async def analyze(self, nickname: str) -> MapsInsight:
        """Возвращает инсайты по картам игрока (best/worst)."""
        player = await self.player_service.get_or_create_player(nickname=nickname)
        maps_stats = await self.maps_service.get_or_fetch_maps_stats(player.player_id)

        snapshots = [
            MapStatSnapshot(
                map_name=m.map_name,
                winrate=m.winrate,
                matches=m.matches,
            )
            for m in maps_stats
        ]
        insight = analyze_maps(snapshots)

        return MapsInsight(
            best=MapInsightItem(
                map=insight.best.map_name,
                winrate=insight.best.winrate,
                matches=insight.best.matches,
            ),
            worst=MapInsightItem(
                map=insight.worst.map_name,
                winrate=insight.worst.winrate,
                matches=insight.worst.matches,
            ),
        )
