"""Сервис для управления бизнес-логикой игроков."""

from datetime import datetime, timezone

from loguru import logger
from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.core.settings import db_helper
from app.core.config import settings
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
        bg_tasks: BackgroundTasks,
        redis: Redis,
    ):
        self.session = session
        self.player_repo = player_repo
        self.faceit_client = faceit_client
        self.bg_tasks = bg_tasks
        self.redis = redis

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

    async def get_or_fetch_player(self, nickname: str) -> PlayerDomainModel:
        """Возвращает профиль. Если его нет/устарел - обновляет в фоне."""
        player = await self.player_repo.get_by_nickname(nickname)

        if player:  # Если игрок есть в базе
            if not self._is_cache_stale(player.updated_at):  # Если кэш свежий
                return player

            # Если кэш есть, но протух (Stale-While-Revalidate)
            lock_key = f"lock:player_update:{nickname.lower()}"
            is_locked = await self.redis.set(lock_key, "1", nx=True, ex=300)
            if is_locked:
                self.bg_tasks.add_task(self._refresh_player_bg, nickname, lock_key)
            else:
                logger.debug(
                    f"Обновление {nickname} уже идет в другом процессе. Пропускаем."
                )

            return player  # Отдаем старые данные мгновенно

        # Если игрока вообще нет — жесткий синк
        raw_player_data = await self.faceit_client.get_player(nickname)
        return await self.create_or_update_from_faceit(player_data=raw_player_data)

    async def _refresh_player_bg(self, nickname: str, lock_key: str) -> None:
        """Фоновое обновление профиля игрока (изолировано от HTTP-запроса)."""
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
