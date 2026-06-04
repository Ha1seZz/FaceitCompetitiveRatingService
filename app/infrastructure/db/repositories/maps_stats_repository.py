"""Репозиторий для работы со статистикой игрока по картам в БД."""

from sqlalchemy import delete, insert, select
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
        if not instances:
            return

        # Конвертируем объекты ORM в плоские словари для генерации многострочного INSERT
        mappings = [
            {
                "id": inst.id,
                "map_name": inst.map_name,
                "matches": inst.matches,
                "won": inst.won,
                "lost": inst.lost,
                "winrate": inst.winrate,
                "average_kills": inst.average_kills,
                "average_deaths": inst.average_deaths,
                "average_kd_ratio": inst.average_kd_ratio,
                "average_kr_ratio": inst.average_kr_ratio,
                "hs": inst.hs,
                "adr": inst.adr,
                "rounds": inst.rounds,
                "kills": inst.kills,
                "assists": inst.assists,
                "deaths": inst.deaths,
                "headshots": inst.headshots,
                "total_damage": inst.total_damage,
                "penta_kills": inst.penta_kills,
                "player_id": inst.player_id,
                "updated_at": inst.updated_at,
            }
            for inst in instances
        ]

        await self.session.execute(insert(MapStat), mappings)
