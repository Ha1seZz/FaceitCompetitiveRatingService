"""Use-case анализа игрока."""

from app.schemas.maps_insight import MapsInsight
from app.infrastructure.faceit.client import FaceitClient
from app.application.maps_stats_service import MapsStatsService
from app.application.player_service import PlayerService
from app.domain.maps.analysis import analyze_maps


class PlayerAnalysisService:  # ← Use Case

    def __init__(
        self,
        faceit_client: FaceitClient,
        maps_service: MapsStatsService,
        player_service: PlayerService,
    ):
        self.faceit_client = faceit_client
        self.maps_service = maps_service
        self.player_service = player_service

    async def analyze(self, nickname: str) -> MapsInsight:
        """Возвращает инсайты по картам игрока (best/worst)."""
        # Оркестрация 3х операций:
        player = await self.player_service.get_or_create_player(nickname=nickname)
        maps_stats = await self.maps_service.get_or_fetch_maps_stats(player.player_id)
        maps_insight = analyze_maps(maps_stats)  # ← Domain
        return maps_insight
