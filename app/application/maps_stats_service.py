"""Сервис кэширования и выдачи статистики игрока по картам."""

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.infrastructure.db.repositories import MapsStatsRepository
from app.infrastructure.faceit.client import FaceitClient
from app.infrastructure.faceit.parsers import parse_faceit_map_stats
from app.domain.maps.models import (
    MapStatDomainModel,
    MapStatSnapshot,
    MapsInsightSnapshot,
)
from app.domain.maps.analysis import analyze_maps
from app.core.config import settings


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
        max_age_minutes: int = 30,
    ) -> list[MapStatDomainModel]:
        """Получить статистику по картам для игрока."""
        cached_stats = await self.repository.get_by_player_id(player_id)

        if cached_stats and not self._is_stale(cached_stats, max_age_minutes):
            return cached_stats

        raw_stats = await self.faceit_client.get_player_maps_stats_raw(player_id)
        return await self._save_stats(player_id, raw_stats)

    async def _save_stats(
        self,
        player_id: str,
        raw_stats: dict,
    ) -> list[MapStatDomainModel]:
        """Сохраняет статистику в БД."""
        TARGET_MODE = "5v5"
        unique_maps: dict[str, dict] = {}

        for segment in raw_stats.get("segments", []):
            # Отсекаем всё, что не является картой или нужным режимом
            if segment.get("type") != "Map" or segment.get("mode") != TARGET_MODE:
                continue

            map_name = segment.get("label")
            if not map_name:
                continue

            if map_name in unique_maps:
                logger.warning(
                    "Обнаружен дубликат карты {map_name} для режима 5v5. "
                    "Выбираем запись с наибольшим количеством матчей.",
                    map_name=map_name
                )
                # Сравниваем количество матчей, оставляем лучшую запись
                current_matches = int(segment.get("stats", {}).get("Matches", 0))
                existing_matches = int(
                    unique_maps[map_name].get("stats", {}).get("Matches", 0)
                )

                if current_matches <= existing_matches:
                    continue

            unique_maps[map_name] = segment

        segments = list(unique_maps.values())

        # Защитная проверка на случай, если Faceit отдал пустой массив или изменил API
        if not segments and raw_stats.get("segments"):
            logger.error(
                "API Faceit вернул сегменты, но ни один не подошел под фильтр соревновательных карт. "
                "Возможно, изменился формат ответа API!"
            )

        insert_data = []
        for stat in segments:
            parsed_stat = parse_faceit_map_stats(stat)
            parsed_stat["player_id"] = player_id
            insert_data.append(parsed_stat)

        updated_models = await self.repository.bulk_upsert(insert_data)
        await self.session.commit()
        return updated_models

    async def analyze(self, player_id: str) -> MapsInsightSnapshot:
        """Анализирует карты игрока (best/worst/reliable)."""
        maps_stats = await self.get_or_fetch_maps_stats(player_id)

        snapshots = [
            MapStatSnapshot(
                map_name=m.map_name,
                winrate=m.winrate,
                matches=m.matches,
            )
            for m in maps_stats
        ]
        return analyze_maps(
            snapshots,
            settings.player.min_matches_for_analysis,
        )

    def _is_stale(self, stats: list[MapStatDomainModel], max_age_minutes: int) -> bool:
        """Проверяет устарел ли кеш."""
        if not stats:
            return True

        # Кэш считается свежим, если самый последний updated_at среди записей моложе max_age_minutes
        latest = max(s.updated_at for s in stats)
        age = datetime.now(timezone.utc) - latest
        return age.total_seconds() > max_age_minutes * 60
