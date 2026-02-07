"""Репозиторий для работы со статистикой игрока по картам в БД."""

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import MapStat


class MapsStatsRepository:
    """Обеспечивает доступ к данным статистики карт и операции удаления/создания."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_player_id(self, player_id: str) -> list[MapStat]:
        """Извлекает полный список статистики по картам для конкретного игрока."""
        stmt = select(MapStat).where(MapStat.player_id == player_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_by_player_id(self, player_id: str) -> None:
        """Удаляет всю имеющуюся статистику карт игрока перед обновлением кэша."""
        await self.session.execute(
            delete(MapStat).where(MapStat.player_id == player_id)
        )

    async def bulk_create(self, instances: list[MapStat]) -> None:
        """Выполняет массовое добавление новых записей статистики в сессию."""
        self.session.add_all(instances)
