"""Сервис кэширования истории матчей игрока."""

from datetime import datetime, timezone

from loguru import logger
from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.settings import db_helper
from app.domain.time_analysis.analysis import build_time_snapshot
from app.infrastructure.db.repositories import MatchHistoryRepository, PlayerRepository
from app.infrastructure.faceit.client import FaceitClient
from app.schemas import MatchHistoryRow


class MatchHistoryService:
    """Application-сервис: загрузка/кэширование истории матчей игрока для аналитики."""

    _updating_players: set[str] = set()

    def __init__(
        self,
        match_history_repo: MatchHistoryRepository,
        player_repo: PlayerRepository,
        faceit_client: FaceitClient,
        session: AsyncSession,
        bg_tasks: BackgroundTasks,
    ):
        self.match_history_repo = match_history_repo
        self.player_repo = player_repo
        self.faceit_client = faceit_client
        self.session = session
        self.bg_tasks = bg_tasks

    async def get_or_fetch_match_history(
        self,
        player_id: str,
        updated_at: datetime,
        match_limit: int = None,
    ) -> list[MatchHistoryRow]:
        """Возвращает историю матчей игрока."""

        limit = match_limit or settings.match_history.limit
        cached_rows = await self.match_history_repo.get_last(
            player_id=player_id,
            limit=limit,
        )

        if cached_rows:  # Если кэш есть
            if not self._is_cache_stale(updated_at):  # Если кэш свежий
                return cached_rows

            # Если кэш есть, но протух (Stale-While-Revalidate)
            elif player_id not in self.__class__._updating_players:
                self.__class__._updating_players.add(player_id)
                self.bg_tasks.add_task(
                    self._refresh_match_history_bg,
                    player_id,
                    limit,
                )
            return cached_rows  # Отдаем старые данные мгновенно

        # Если кэша вообще нет — жесткий синк
        fast_limit = 100
        await self._refresh_match_history_sync(player_id, fast_limit)

        if limit > fast_limit:
            if player_id not in self.__class__._updating_players:
                self.__class__._updating_players.add(player_id)
                self.bg_tasks.add_task(
                    self._refresh_match_history_bg,
                    player_id,
                    limit,
                    start_offset=fast_limit,
                )

        return await self.match_history_repo.get_last(player_id=player_id, limit=limit)

    async def _refresh_match_history_sync(self, player_id: str, limit: int) -> None:
        """Синхронное обновление кэша (для новых игроков)."""
        raw_matches = await self.faceit_client.get_player_match_history(
            player_id,
            max_matches=limit,
        )

        rows = self._parse_raw_matches_static(raw_matches, player_id)
        await self.match_history_repo.add_new_matches(player_id=player_id, rows=rows)
        await self.session.commit()

    async def _refresh_match_history_bg(
        self,
        player_id: str,
        limit: int,
        start_offset: int = 0,
    ) -> None:
        """Автономная фоновая задача. Создает свою собственную изолированную сессию."""

        async with db_helper.session_factory() as session:
            bg_match_repo = MatchHistoryRepository(session)
            bg_player_repo = PlayerRepository(session)

            try:
                raw_matches = await self.faceit_client.get_player_match_history(
                    player_id,
                    max_matches=limit,
                    start_offset=start_offset,
                )
                rows = self._parse_raw_matches_static(raw_matches, player_id)
                await bg_match_repo.add_new_matches(player_id=player_id, rows=rows)
                await bg_player_repo.set_match_history_updated_at(
                    player_id,
                    datetime.now(timezone.utc),
                )

                await session.commit()
                logger.info(
                    "Фоновое обновление успешно завершено для {player_id}",
                    player_id=player_id,
                )

            except Exception as e:
                await session.rollback()
                logger.error(
                    "Ошибка при фоновом обновлении кэша для {player_id}: {e}",
                    player_id=player_id,
                    e=e,
                )

            finally:
                self.__class__._updating_players.discard(player_id)

    @staticmethod
    def _parse_raw_matches_static(
        raw_matches: list,
        player_id: str,
    ) -> list[MatchHistoryRow]:
        """Вспомогательный метод парсинга сырых данных Faceit."""
        rows: list[MatchHistoryRow] = []

        for match in raw_matches:
            try:
                match_id = match.get("match_id")
                if not match_id:
                    continue

                snapshot = build_time_snapshot(match, player_id)
                if snapshot.is_win is None:
                    continue

                rows.append(
                    MatchHistoryRow(
                        match_id=match_id,
                        finished_at_utc=snapshot.finished_at_utc,
                        is_win=snapshot.is_win,
                    )
                )
            except ValueError:
                continue

        return rows

    def _is_cache_stale(self, updated_at: datetime | None) -> bool:
        """True, если кэш отсутствует или старше TTL."""
        if not updated_at:
            return True

        age = datetime.now(timezone.utc) - updated_at
        return age > settings.match_history.ttl
