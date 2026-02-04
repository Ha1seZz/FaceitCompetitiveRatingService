"""Репозиторий для работы со статистикой игрока по картам в БД."""

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.map_stat import MapStat


class MapsStatsRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_player_id(self, player_id: str) -> list[MapStat]:
        stmt = select(MapStat).where(MapStat.player_id == player_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_by_player_id(self, player_id: str) -> None:
        stmt = delete(MapStat).where(MapStat.player_id == player_id)
        await self.session.execute(stmt)

    async def bulk_create(self, stats: list[MapStat]) -> None:
        self.session.add_all(stats)
