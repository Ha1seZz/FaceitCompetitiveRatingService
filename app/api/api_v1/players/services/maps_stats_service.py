"""Сервис для работы со статистикой по картам."""

from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.api_v1.players.maps_stats_repository import MapsStatsRepository
from app.api.api_v1.players.schemas import MapStatsCreate, MapStatsResponse
from app.services.faceit.client import FaceitClient
from app.core.models import MapStat


class MapsStatsService:
    """Класс-сервис для получения и кеширования статистики по картам."""

    def __init__(
        self,
        session: AsyncSession,
        repository: MapsStatsRepository,
        faceit_client: FaceitClient,
    ):
        self.session = session
        self.repository = repository
        self.faceit_client = faceit_client

    async def get_or_fetch_maps_stats(
        self,
        player_id: str,
        max_age_minutes: int = 15,
    ) -> list[MapStatsResponse]:
        """Получить статистику по картам для игрока."""
        cached_stats = await self.repository.get_by_player_id(player_id)

        if cached_stats and not self._is_stale(cached_stats, max_age_minutes):
            return [MapStatsResponse.model_validate(s) for s in cached_stats]

        raw_stats = await self.faceit_client.get_player_maps_stats_raw(player_id)
        db_instances = await self._save_stats(player_id, raw_stats)
        return [MapStatsResponse.model_validate(s) for s in db_instances]

    async def _save_stats(
        self,
        player_id: str,
        raw_stats: dict,
    ) -> list[MapStat]:
        """Сохраняет статистику в БД."""
        segments = [s for s in raw_stats.get("segments", []) if s.get("type") == "Map"]
        validated_schemas = [MapStatsCreate(**stat) for stat in segments]

        await self.repository.delete_by_player_id(player_id)

        db_instances = [
            MapStat(**schema.model_dump(), player_id=player_id)
            for schema in validated_schemas
        ]

        await self.repository.bulk_create(db_instances)
        return db_instances

    def _is_stale(self, stats: list, max_age_minutes: int) -> bool:
        """Проверяет устарел ли кеш."""
        if not stats:
            return True

        latest = max(s.updated_at for s in stats)  # Берём позднее время обновления
        age = datetime.now(timezone.utc) - latest
        return age.total_seconds() > max_age_minutes * 60
