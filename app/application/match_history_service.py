"""Сервис кэширования истории матчей игрока."""

from datetime import datetime, timezone

from arq import ArqRedis
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.core.config import settings
from app.core.exceptions import QueueServiceUnavailableError, ResourceLockedError
from app.domain.time_analysis.analysis import build_time_snapshot
from app.infrastructure.db.repositories import MatchHistoryRepository, PlayerRepository
from app.infrastructure.faceit.client import FaceitClient
from app.schemas import MatchHistoryRow


class MatchHistoryService:
    """Application-сервис: загрузка/кэширование истории матчей игрока для аналитики."""

    def __init__(
        self,
        match_history_repo: MatchHistoryRepository,
        player_repo: PlayerRepository,
        faceit_client: FaceitClient,
        session: AsyncSession,
        redis: Redis,
        arq_pool: ArqRedis | None = None,
    ):
        self.match_history_repo = match_history_repo
        self.player_repo = player_repo
        self.faceit_client = faceit_client
        self.session = session
        self.redis = redis
        self.arq_pool = arq_pool

    async def get_or_fetch_match_history(
        self,
        player_id: str,
        updated_at: datetime | None,
        match_limit: int = None,
    ) -> list[MatchHistoryRow]:
        """Возвращает историю матчей игрока, при необходимости запуская обновление."""
        limit = match_limit or settings.match_history.limit
        cached_rows = await self.match_history_repo.get_last(
            player_id=player_id,
            limit=limit,
        )

        lock_key = f"lock:match_history:{player_id}"

        if cached_rows:
            if not self._is_cache_stale(updated_at):
                return cached_rows

            is_locked = await self.redis.set(lock_key, "1", nx=True, ex=600)
            if is_locked:
                await self._enqueue_refresh(
                    player_id=player_id,
                    limit=limit,
                    start_offset=0,
                    lock_key=lock_key,
                )
            return cached_rows

        is_locked = await self.redis.set(lock_key, "1", nx=True, ex=600)

        if not is_locked:
            logger.warning(
                "Блокировка первичной загрузки. Запрос для {player_id} отклонен.",
                player_id=player_id,
            )
            raise ResourceLockedError(
                "Идет первичная загрузка данных игрока. Повторите запрос через 5 секунд."
            )

        try:
            fast_limit = 100  # Если кэша вообще нет — жесткий синк
            await self.fetch_and_save_matches(player_id, fast_limit)

            if limit > fast_limit:
                await self.redis.expire(lock_key, 600)
                await self._enqueue_refresh(
                    player_id=player_id,
                    limit=limit,
                    start_offset=fast_limit,
                    lock_key=lock_key,
                )
            else:
                await self.redis.delete(lock_key)
        except Exception as e:
            await self.redis.delete(lock_key)
            raise e

        return await self.match_history_repo.get_last(player_id=player_id, limit=limit)

    async def _enqueue_refresh(
        self,
        player_id: str,
        limit: int,
        start_offset: int,
        lock_key: str,
    ) -> None:
        """Отправляет задачу фонового обновления в очередь ARQ."""
        if not self.arq_pool:
            logger.critical(
                "ARQ Redis pool не инициализирован! Фоновая задача для {player_id} не создана.",
                player_id=player_id,
            )
            raise QueueServiceUnavailableError(
                "Сервис фоновых задач не инициализирован"
            )

        try:
            await self.arq_pool.enqueue_job(
                "task_refresh_match_history",
                player_id=player_id,
                limit=limit,
                start_offset=start_offset,
                lock_key=lock_key,
            )
            logger.info(
                "Задача на обновление истории матчей успешно создана для {player_id}",
                player_id=player_id,
            )
        except Exception as e:
            logger.error(
                "Сбой при отправке задачи в Redis для {player_id}: {e}",
                player_id=player_id,
                e=e,
                exc_info=True,
            )
            raise QueueServiceUnavailableError(
                "Не удалось отправить задачу в очередь"
            ) from e

    async def fetch_and_save_matches(
        self,
        player_id: str,
        limit: int,
        start_offset: int = 0,
    ) -> None:
        """
        Универсальный метод скачивания и сохранения.
        Работает с инжектированной self.session.
        """
        async for raw_matches in self.faceit_client.get_player_match_history(
            player_id=player_id,
            max_matches=limit,
            start_offset=start_offset,
        ):
            rows = self._parse_raw_matches_static(raw_matches, player_id)
            if not rows:
                continue

            await self.match_history_repo.add_new_matches(
                player_id=player_id,
                rows=rows,
            )
            await self.session.commit()

        await self.player_repo.set_match_history_updated_at(
            player_id=player_id,
            updated_at=datetime.now(timezone.utc),
        )
        await self.session.commit()

    async def process_background_refresh(
        self,
        player_id: str,
        limit: int,
        start_offset: int,
        lock_key: str,
    ) -> None:
        """
        Метод-обертка специально для вызова из ARQ-воркера.
        Гарантирует снятие блокировки в Redis после выполнения или падения задачи.
        """
        try:
            await self.fetch_and_save_matches(player_id, limit, start_offset)
            logger.info(
                "Фоновое обновление успешно завершено для {player_id}",
                player_id=player_id,
            )
        except Exception as e:
            await self.session.rollback()
            logger.error(
                "Ошибка при фоновом обновлении кэша для {player_id}: {e}",
                player_id=player_id,
                e=e,
            )
            raise e
        finally:
            await self.redis.delete(lock_key)

    @staticmethod
    def _parse_raw_matches_static(
        raw_matches: list,
        player_id: str,
    ) -> list[MatchHistoryRow]:
        """Вспомогательный метод парсинга сырых данных Faceit."""
        rows: list[MatchHistoryRow] = []

        for match in raw_matches:
            try:
                match_id = match.get("match_id")
                if not match_id:
                    continue

                snapshot = build_time_snapshot(match, player_id)
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
                continue
        return rows

    def _is_cache_stale(self, updated_at: datetime | None) -> bool:
        """True, если кэш отсутствует или старше TTL."""
        if not updated_at:
            return True
        age = datetime.now(timezone.utc) - updated_at
        return age > settings.match_history.ttl
