"""Репозиторий кэша истории матчей игрока."""

from typing import Sequence

from sqlalchemy import delete, func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import MatchHistoryRow
from app.infrastructure.db.models import PlayerMatchHistory


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
                match_id=match_id, finished_at_utc=finished_at_utc, is_win=is_win
            )
            for (match_id, finished_at_utc, is_win) in result.all()
        ]

    async def replace(self, player_id: str, rows: Sequence[MatchHistoryRow]) -> int:
        """Полностью заменить историю матчей игрока."""
        await self.session.execute(
            delete(PlayerMatchHistory).where(PlayerMatchHistory.player_id == player_id)
        )

        objects = [
            PlayerMatchHistory(
                player_id=player_id,
                match_id=row.match_id,
                finished_at_utc=row.finished_at_utc,
                is_win=row.is_win,
            )
            for row in rows
        ]
        self.session.add_all(objects)
        return len(objects)

    async def count(self, player_id: str) -> int:
        """Вернуть количество строк истории матчей для игрока."""
        stmt = (
            select(func.count())
            .select_from(PlayerMatchHistory)
            .where(PlayerMatchHistory.player_id == player_id)
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one())
