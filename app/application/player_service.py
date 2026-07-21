"""Сервис для управления бизнес-логикой игроков."""

from datetime import datetime, timezone

from arq import ArqRedis
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.core.settings import db_helper
from app.core.config import settings
from app.core.exceptions import QueueServiceUnavailableError
from app.domain.player.models import PlayerDomainModel
from app.infrastructure.db.repositories import PlayerRepository
from app.infrastructure.faceit.client import FaceitClient
from app.schemas import PlayerCreate


class PlayerService:
    """Application-сервис для обработки операций с игроками."""

    def __init__(
        self,
        session: AsyncSession,
        player_repo: PlayerRepository,
        faceit_client: FaceitClient,
        redis: Redis,
        arq_pool: ArqRedis | None = None,
    ):
        self.session = session
        self.player_repo = player_repo
        self.faceit_client = faceit_client
        self.redis = redis
        self.arq_pool = arq_pool

    async def get_or_fetch_player(self, nickname: str) -> PlayerDomainModel:
        """Возвращает профиль. Если его нет/устарел - обновляет в фоне."""
        cached_player = await self.player_repo.get_by_nickname(nickname)

        if cached_player:
            if not self._is_cache_stale(cached_player.updated_at):
                return cached_player

            lock_key = f"lock:player_update:{nickname.lower()}"
            is_locked = await self.redis.set(lock_key, "1", nx=True, ex=300)
            if is_locked:
                await self._enqueue_refresh(
                    nickname=nickname,
                    lock_key=lock_key,
                )
            return cached_player

        # Если кэша вообще нет — жесткий синк
        raw_player_data = await self.faceit_client.get_player(nickname)
        return await self.create_or_update_from_faceit(player_data=raw_player_data)

    async def _enqueue_refresh(self, nickname: str, lock_key: str) -> None:
        """
        Отправляет задачу фонового обновления в очередь ARQ.

        Выбрасывает QueueServiceUnavailableError, если пул не инициализирован
        или брокер сообщений недоступен, предотвращая тихие отказы.
        """
        if not self.arq_pool:
            logger.critical(
                "ARQ Redis pool не инициализирован! Фоновая задача для {nickname} не может быть создана.",
                nickname=nickname,
            )
            raise QueueServiceUnavailableError(
                "Сервис фоновых задач не инициализирован"
            )

        try:
            await self.arq_pool.enqueue_job(
                "task_refresh_player",
                nickname=nickname,
                lock_key=lock_key,
            )
            logger.info(
                "Задача на обновление информации о игроке успешно создана для {nickname}",
                nickname=nickname,
            )
        except Exception as e:
            logger.error(
                "Сбой при отправке задачи в Redis для {nickname}: {e}",
                nickname=nickname,
                e=e,
                exc_info=True,
            )
            raise QueueServiceUnavailableError(
                "Не удалось отправить задачу в очередь"
            ) from e

    async def create_or_update_from_faceit(
        self,
        player_data: dict,
    ) -> PlayerDomainModel:
        """Синхронизирует данные, полученные из внешнего API, сохраняя в БД."""
        validated = PlayerCreate(**player_data)
        clean_data = validated.model_dump(exclude_unset=True)
        player_domain = await self.player_repo.upsert_from_faceit_data(clean_data)
        await self.session.commit()
        return player_domain

    async def _refresh_player_bg(self, nickname: str, lock_key: str) -> None:
        """
        Фоновая задача обновления данных.

        Выполняется воркером ARQ. Создает собственную изолированную сессию БД,
        так как жизненный цикл задачи не привязан к HTTP-запросу.
        """
        async with db_helper.session_factory() as session:
            bg_repo = PlayerRepository(session)

            try:
                raw_player_data = await self.faceit_client.get_player(nickname)
                validated = PlayerCreate(**raw_player_data)
                clean_data = validated.model_dump(exclude_unset=True)

                await bg_repo.upsert_from_faceit_data(clean_data)
                await session.commit()
                logger.info(
                    "Фоновое обновление профиля завершено для {nickname}",
                    nickname=nickname,
                )
            except Exception as e:
                await session.rollback()
                logger.error(
                    "Ошибка при фоновом обновлении профиля {nickname}: {e}",
                    e=e,
                )
            finally:
                await self.redis.delete(lock_key)

    async def get_players(
        self,
        limit: int,
        cursor: str | None = None,
    ) -> list[PlayerDomainModel]:
        """Получает список всех игроков."""
        return await self.player_repo.get_all(limit=limit, cursor=cursor)

    async def delete_player_by_nickname(self, nickname: str) -> None:
        """Удаляет игрока или выбрасывает доменную ошибку, если игрок не найден."""
        await self.player_repo.delete_player(nickname=nickname)
        await self.session.commit()

    def _is_cache_stale(self, updated_at: datetime | None) -> bool:
        """True, если кэш отсутствует или старше TTL."""
        if not updated_at:
            return True

        age = datetime.now(timezone.utc) - updated_at
        return age > settings.player.ttl
