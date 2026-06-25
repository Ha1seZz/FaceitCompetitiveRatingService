"""Репозиторий для работы с игроками в базе данных."""

from datetime import datetime

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import func, select, delete, update as sql_update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.player.models import PlayerDomainModel
from app.infrastructure.db.models import Player


class PlayerRepository:
    """Класс для управления жизненным циклом объектов Player в БД."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _map_to_domain(self, player_orm: Player | None) -> PlayerDomainModel | None:
        """Транслирует ORM-модель SQLAlchemy в чистый доменный датакласс."""
        if not player_orm:
            return None

        return PlayerDomainModel(
            nickname=player_orm.nickname,
            verified=player_orm.verified,
            faceit_url=player_orm.faceit_url,
            player_id=player_orm.player_id,
            friends_count=player_orm.friends_count,
            activated_at=player_orm.activated_at,
            skill_level=player_orm.skill_level,
            faceit_elo=player_orm.faceit_elo,
            region=player_orm.region,
            country=player_orm.country,
            steam_nickname=player_orm.steam_nickname,
            steam_id_64=player_orm.steam_id_64,
            updated_at=player_orm.updated_at,
            match_history_updated_at=player_orm.match_history_updated_at,
        )

    async def get_all(self, limit: int, offset: int) -> list[PlayerDomainModel]:
        """Возвращает список игроков с поддержкой пагинации."""
        stmt = select(Player).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return [self._map_to_domain(p) for p in result.scalars().all()]

    async def get_by_nickname(self, nickname: str) -> PlayerDomainModel | None:
        """Выполняет поиск игрока по его текущему никнейму."""
        stmt = select(Player).where(Player.nickname == nickname)
        result = await self.session.execute(stmt)
        return self._map_to_domain(result.scalar_one_or_none())

    async def set_match_history_updated_at(
        self,
        player_id: str,
        updated_at: datetime,
    ) -> bool:
        """Установить timestamp обновления истории матчей."""
        stmt = (
            sql_update(Player)
            .where(Player.player_id == player_id)
            .values(match_history_updated_at=updated_at)
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def upsert_from_faceit_data(self, data: dict) -> PlayerDomainModel:
        """Атомарно сохраняет или обновляет игрока в БД."""
        stmt = pg_insert(Player).values(**data)

        update_attrs = {key: value for key, value in data.items() if key != "player_id"}
        update_attrs["updated_at"] = func.now()

        stmt = stmt.on_conflict_do_update(
            index_elements=[Player.player_id],
            set_=update_attrs,
        ).returning(Player)

        result = await self.session.execute(stmt)
        return self._map_to_domain(result.scalar_one())

    async def delete_player(self, nickname: str) -> None:
        """
        Удаляет игрока из базы данных по его nickname.
        """
        stmt = delete(Player).where(Player.nickname == nickname)
        await self.session.execute(stmt)
