"""Сервис для управления бизнес-логикой игроков."""

from datetime import datetime, timezone

from loguru import logger
from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import db_helper
from app.core.config import settings
from app.core.exceptions import PlayerNotFoundError
from app.domain.player.models import PlayerDomainModel
from app.infrastructure.db.repositories import PlayerRepository
from app.infrastructure.faceit.client import FaceitClient
from app.schemas.players import PlayerCreate


class PlayerService:
    """Класс-сервис для обработки операций с игроками."""

    _updating_profiles: set[str] = set()

    def __init__(
        self,
        session: AsyncSession,
        repository: PlayerRepository,
        faceit_client: FaceitClient,
        bg_tasks: BackgroundTasks,
    ):
        self.session = session
        self.repository = repository
        self.faceit_client = faceit_client
        self.bg_tasks = bg_tasks

    async def create_or_update_from_faceit(
        self,
        player_data: dict,
    ) -> PlayerDomainModel:
        """Синхронизирует данные, полученные из внешнего API, сохраняя в БД."""
        validated = PlayerCreate(**player_data)
        clean_data = validated.model_dump(exclude_unset=True)
        player_domain = await self.repository.upsert_from_faceit_data(clean_data)
        await self.session.commit()
        return player_domain

    async def get_or_fetch_player(self, nickname: str) -> PlayerDomainModel:
        """Возвращает профиль. Если его нет/устарел — обновляет в фоне."""
        player = await self.repository.get_by_nickname(nickname)

        if player:  # Если игрок есть в базе
            if not self._is_cache_stale(player.updated_at):  # Если кэш свежий
                return player

            # Кэш устарел. Проверяем, не обновляется ли он уже в фоне
            if nickname not in self.__class__._updating_profiles:
                self.__class__._updating_profiles.add(nickname)
                self.bg_tasks.add_task(self._refresh_player_bg, nickname)

            return player  # Отдаем старые данные мгновенно

        # Игрока нет в базе
        raw_player_data = await self.faceit_client.get_player(nickname)
        return await self.create_or_update_from_faceit(player_data=raw_player_data)

    async def _refresh_player_bg(self, nickname: str) -> None:
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
                self.__class__._updating_profiles.discard(nickname)

    async def get_players(self, limit: int, offset: int) -> list[PlayerDomainModel]:
        """Получает список всех игроков."""
        return await self.repository.get_all(limit=limit, offset=offset)

    async def delete_player(self, player_id: str) -> None:
        """Удаляет игрока или выбрасывает доменную ошибку, если игрок не найден."""
        success = await self.repository.delete_player(player_id=player_id)

        if not success:
            raise PlayerNotFoundError(player_id=player_id)

        await self.session.commit()

    def _is_cache_stale(self, updated_at: datetime | None) -> bool:
        """True, если кэш отсутствует или старше TTL."""
        if not updated_at:
            return True

        age = datetime.now(timezone.utc) - updated_at
        return age > settings.player.ttl
