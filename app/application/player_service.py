"""Сервис для управления бизнес-логикой игроков."""

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import PlayerNotFoundError
from app.domain.player.models import PlayerDomainModel
from app.infrastructure.db.repositories import PlayerRepository
from app.infrastructure.faceit.client import FaceitClient
from app.schemas.players import PlayerCreate


class PlayerService:
    """Класс-сервис для обработки операций с игроками."""

    def __init__(
        self,
        session: AsyncSession,
        repository: PlayerRepository,
        faceit_client: FaceitClient,
    ):
        self.session = session
        self.repository = repository
        self.faceit_client = faceit_client

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

    async def get_or_create_player(self, nickname: str) -> PlayerDomainModel:
        """Возвращает игрока, а если его нет/кэш устарел — подтягивает из Faceit."""
        player = await self.repository.get_by_nickname(nickname)

        if player:
            if not self._is_cache_stale(player.updated_at):  # Если кэш свежий
                return player

        raw_player_data = await self.faceit_client.get_player(nickname)
        return await self.create_or_update_from_faceit(player_data=raw_player_data)

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
