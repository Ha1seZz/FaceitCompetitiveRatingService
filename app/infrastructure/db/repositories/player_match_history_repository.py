"""Репозиторий кэша истории матчей игрока."""

from typing import Sequence

from sqlalchemy import func, select, desc
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import PlayerMatchHistory
from app.schemas import MatchHistoryRow


class MatchHistoryRepository:
    """Репозиторий истории матчей игрока (PlayerMatchHistory)."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_last(self, player_id: str, limit: int) -> list[MatchHistoryRow]:
        """Вернуть последние матчи игрока в порядке от новых к старым."""
        stmt = (
            select(
                PlayerMatchHistory.match_id,
                PlayerMatchHistory.finished_at_utc,
                PlayerMatchHistory.is_win,
            )
            .where(PlayerMatchHistory.player_id == player_id)
            .order_by(
                desc(PlayerMatchHistory.finished_at_utc),
                desc(PlayerMatchHistory.match_id),
            )
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return [
            MatchHistoryRow(
                match_id=match_id,
                finished_at_utc=finished_at_utc,
                is_win=is_win,
            )
            for (match_id, finished_at_utc, is_win) in result.all()
        ]

    async def add_new_matches(
        self,
        player_id: str,
        rows: Sequence[MatchHistoryRow],
    ) -> None:
        """Вставляет только новые матчи, игнорируя те, что уже есть в базе."""
        if not rows:
            return

        insert_data = [
            {
                "player_id": player_id,
                "match_id": row.match_id,
                "finished_at_utc": row.finished_at_utc,
                "is_win": row.is_win,
            }
            for row in rows
        ]

        stmt = pg_insert(PlayerMatchHistory).values(insert_data)

        stmt = stmt.on_conflict_do_nothing(index_elements=["player_id", "match_id"])

        await self.session.execute(stmt)

    async def count(self, player_id: str) -> int:
        """Вернуть количество строк истории матчей для игрока."""
        stmt = (
            select(func.count())
            .select_from(PlayerMatchHistory)
            .where(PlayerMatchHistory.player_id == player_id)
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one())
