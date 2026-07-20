"""Сервис для управления статистикой игрока."""

from datetime import datetime, timezone

from arq import ArqRedis
from loguru import logger
from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.core.settings import db_helper
from app.core.config import settings
from app.domain.player.models import PlayerStatsDomainModel
from app.infrastructure.db.repositories import PlayerStatsRepository
from app.infrastructure.faceit.client import FaceitClient


class PlayerStatsService:
    """Сервис для управления статистикой игрока."""

    def __init__(
        self,
        stats_repo: PlayerStatsRepository,
        faceit_client: FaceitClient,
        session: AsyncSession,
        redis: Redis,
        arq_pool: ArqRedis | None = None,
        bg_tasks: BackgroundTasks | None = None,
    ):
        self.stats_repo = stats_repo
        self.faceit_client = faceit_client
        self.session = session
        self.redis = redis
        self.arq_pool = arq_pool
        self.bg_tasks = bg_tasks

    async def get_or_fetch_player_stats(
        self,
        player_id: str,
    ) -> PlayerStatsDomainModel:
        """Основной метод: получение статистики игрока с кэшированием."""

        cached_stats = await self.stats_repo.get_by_player_id(player_id)

        if cached_stats and not self._is_cache_stale(cached_stats.updated_at):
            return cached_stats

        if cached_stats:
            lock_key = f"lock:player_stats:{player_id}"
            is_locked = await self.redis.set(lock_key, "1", nx=True, ex=300)

            if is_locked and self.arq_pool:
                await self.arq_pool.enqueue_job(
                    "task_refresh_stats",
                    player_id,
                    lock_key,
                )
            return cached_stats

        # Если кэша вообще нет — жесткий синк
        return await self._refresh_stats_sync(player_id)

    async def _refresh_stats_sync(self, player_id: str) -> PlayerStatsDomainModel:
        """Синхронное обновление кэша (для новых игроков)."""
        raw_data = await self.faceit_client.get_player_stats(
            player_id=player_id,
            max_matches=settings.player_stats.min_matches_for_analysis,
        )
        stats_domain = self._map_to_domain(raw_data, player_id)

        await self.stats_repo.save_stats(player_id=player_id, stats=stats_domain)
        await self.session.commit()
        return stats_domain

    async def _refresh_stats_bg(self, player_id: str, lock_key: str) -> None:
        """Изолированное фоновое обновление."""
        async with db_helper.session_factory() as session:
            bg_repo = PlayerStatsRepository(session)
            try:
                raw_data = await self.faceit_client.get_player_stats(
                    player_id=player_id,
                    max_matches=settings.player_stats.min_matches_for_analysis,
                )
                stats_domain = self._map_to_domain(raw_data, player_id)

                await bg_repo.save_stats(player_id=player_id, stats=stats_domain)
                await session.commit()
                logger.info(
                    "Фоновое обновление статистики успешно завершено для {player_id}",
                    player_id=player_id,
                )
            except Exception as e:
                await session.rollback()
                logger.error(
                    "Ошибка обновления статистики для {player_id}: {e}",
                    player_id=player_id,
                    e=e,
                )
            finally:
                await self.redis.delete(lock_key)

    def _map_to_domain(self, raw_data: dict, player_id: str) -> PlayerStatsDomainModel:
        """Трансформация внешнего API в Domain Model."""

        items = raw_data.get("items", [])
        total_matches = len(items)

        if total_matches == 0:
            return self._get_empty_stats(player_id)

        wins = 0
        total_kills = 0.0
        total_deaths = 0.0
        total_assists = 0.0
        total_damage = 0.0
        total_headshots_percent = 0.0
        total_kr_ratio = 0.0
        total_kd_ratio = 0.0
        total_adr = 0.0

        for item in items:
            stats = item.get("stats", {})

            if stats.get("Result") == "1":
                wins += 1

            total_kills += float(stats.get("Kills", 0))
            total_deaths += float(stats.get("Deaths", 0))
            total_assists += float(stats.get("Assists", 0))
            total_damage += float(stats.get("Damage", 0))
            total_headshots_percent += float(stats.get("Headshots %", 0))
            total_kr_ratio += float(stats.get("K/R Ratio", 0))
            total_kd_ratio += float(stats.get("K/D Ratio", 0))
            total_adr += float(stats.get("ADR", 0))

        return PlayerStatsDomainModel(
            player_id=player_id,
            matches_analyzed=total_matches,
            winrate=round((wins / total_matches) * 100, 2),
            avg_kills=round(total_kills / total_matches, 2),
            avg_deaths=round(total_deaths / total_matches, 2),
            avg_assists=round(total_assists / total_matches, 2),
            avg_damage=round(total_damage / total_matches, 2),
            kd_ratio=round(total_kd_ratio / total_matches, 2),
            kr_ratio=round(total_kr_ratio / total_matches, 2),
            headshots_percent=round(total_headshots_percent / total_matches, 2),
            adr=round(total_adr / total_matches, 2),
        )

    def _is_cache_stale(self, updated_at: datetime | None) -> bool:
        """Проверка TTL."""
        if not updated_at:
            return True

        age = datetime.now(timezone.utc) - updated_at
        return age > settings.player_stats.ttl

    def _get_empty_stats(self, player_id: str) -> PlayerStatsDomainModel:
        """Возвращает нулевую статистику для игроков без матчей."""

        return PlayerStatsDomainModel(
            player_id=player_id,
            matches_analyzed=0,
            winrate=0.0,
            avg_kills=0.0,
            avg_deaths=0.0,
            avg_assists=0.0,
            avg_damage=0.0,
            kd_ratio=0.0,
            kr_ratio=0.0,
            headshots_percent=0.0,
            adr=0.0,
        )
