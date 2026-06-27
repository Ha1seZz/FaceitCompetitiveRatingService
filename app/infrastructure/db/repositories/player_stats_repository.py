"""Репозиторий для работы со статистикой игроков в базе данных."""

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.player.models import PlayerStatsDomainModel
from app.infrastructure.db.models import PlayerStats


class PlayerStatsRepository:
    """Репозиторий для управления агрегированной статистикой."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_player_id(self, player_id: str) -> PlayerStatsDomainModel | None:
        """Получает статистику игрока по его ID."""
        stmt = select(PlayerStats).where(PlayerStats.player_id == player_id)
        result = await self.session.execute(stmt)
        stats_orm = result.scalar_one_or_none()

        if not stats_orm:
            return None

        return PlayerStatsDomainModel(
            player_id=stats_orm.player_id,
            matches_analyzed=stats_orm.matches_analyzed,
            winrate=stats_orm.winrate,
            avg_kills=stats_orm.avg_kills,
            avg_deaths=stats_orm.avg_deaths,
            avg_assists=stats_orm.avg_assists,
            avg_damage=stats_orm.avg_damage,
            kd_ratio=stats_orm.kd_ratio,
            kr_ratio=stats_orm.kr_ratio,
            headshots_percent=stats_orm.headshots_percent,
            adr=stats_orm.adr,
            updated_at=stats_orm.updated_at,
        )

    async def save_stats(self, player_id: str, stats: PlayerStatsDomainModel) -> None:
        """
        Вставляет новую статистику или обновляет существующую (UPSERT).
        Это атомарная операция, защищенная от race conditions.
        """
        stmt = pg_insert(PlayerStats).values(
            player_id=player_id,
            matches_analyzed=stats.matches_analyzed,
            winrate=stats.winrate,
            avg_kills=stats.avg_kills,
            avg_deaths=stats.avg_deaths,
            avg_assists=stats.avg_assists,
            avg_damage=stats.avg_damage,
            kd_ratio=stats.kd_ratio,
            kr_ratio=stats.kr_ratio,
            headshots_percent=stats.headshots_percent,
            adr=stats.adr,
            updated_at=func.now(),
        )

        stmt = stmt.on_conflict_do_update(
            index_elements=["player_id"],
            set_=stmt.excluded,
        )

        await self.session.execute(stmt)
