"""Репозиторий для работы со статистикой игрока по картам в БД."""

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.domain.maps.models import MapStatDomainModel
from app.infrastructure.db.models import MapStat


class MapsStatsRepository:
    """Обеспечивает доступ к данным статистики карт и операции удаления/создания."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _map_to_domain(self, stat_orm: MapStat) -> MapStatDomainModel:
        """Транслирует ORM-модель в чистый датакласс."""
        return MapStatDomainModel(
            id=stat_orm.id,
            map_name=stat_orm.map_name,
            matches=stat_orm.matches,
            won=stat_orm.won,
            lost=stat_orm.lost,
            winrate=stat_orm.winrate,
            average_kills=stat_orm.average_kills,
            average_deaths=stat_orm.average_deaths,
            average_kd_ratio=stat_orm.average_kd_ratio,
            average_kr_ratio=stat_orm.average_kr_ratio,
            hs=stat_orm.hs,
            adr=stat_orm.adr,
            rounds=stat_orm.rounds,
            kills=stat_orm.kills,
            assists=stat_orm.assists,
            deaths=stat_orm.deaths,
            headshots=stat_orm.headshots,
            total_damage=stat_orm.total_damage,
            penta_kills=stat_orm.penta_kills,
            player_id=stat_orm.player_id,
            updated_at=stat_orm.updated_at,
        )

    async def get_by_player_id(self, player_id: str) -> list[MapStatDomainModel]:
        """Извлекает полный список статистики по картам для конкретного игрока."""
        stmt = select(MapStat).where(MapStat.player_id == player_id)
        result = await self.session.execute(stmt)
        return [self._map_to_domain(m) for m in result.scalars().all()]

    async def bulk_upsert(self, insert_data: list[dict]) -> list[MapStatDomainModel]:
        """Атомарно обновляет или вставляет статистику по картам."""
        if not insert_data:
            return []

        stmt = pg_insert(MapStat).values(insert_data)

        update_attrs = {
            c.name: c
            for c in stmt.excluded
            if c.name not in ("id", "player_id", "map_name")
        }
        update_attrs["updated_at"] = func.now()

        stmt = stmt.on_conflict_do_update(
            index_elements=["player_id", "map_name"],
            set_=update_attrs,
        ).returning(MapStat)

        result = await self.session.execute(stmt)

        return [self._map_to_domain(m) for m in result.scalars().all()]
