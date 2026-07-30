"""Модуль фоновых задач."""

from loguru import logger

from app.infrastructure.db.repositories import (
    PlayerRepository,
    MatchHistoryRepository,
    PlayerStatsRepository,
)
from app.application import MatchHistoryService, PlayerService, PlayerStatsService


async def task_refresh_match_history(
    ctx,
    player_id: str,
    limit: int,
    start_offset: int,
    lock_key: str,
) -> None:
    """Фоновая задача для обновления истории матчей игрока."""
    logger.info(
        "Начало фонового обновления матчей для игрока {player_id}",
        player_id=player_id,
    )
    session_factory = ctx["session_factory"]

    async with session_factory() as session:
        match_history_service = MatchHistoryService(
            match_history_repo=MatchHistoryRepository(session),
            player_repo=PlayerRepository(session),
            faceit_client=ctx["faceit_client"],
            session=session,
            redis=ctx["redis"],
            arq_pool=None,
        )
        await match_history_service.process_background_refresh(
            player_id=player_id,
            limit=limit,
            start_offset=start_offset,
            lock_key=lock_key,
        )
    logger.info(
        "Фоновое обновление матчей для игрока {player_id} завершено.",
        player_id=player_id,
    )


async def task_refresh_player(ctx, nickname: str, lock_key: str) -> None:
    """Фоновая задача для обновления информации о игроке."""
    logger.info(
        "Начало фонового обновления информации о игроке {nickname}",
        nickname=nickname,
    )
    session_factory = ctx["session_factory"]

    async with session_factory() as session:
        service = PlayerService(
            session=session,
            player_repo=PlayerRepository(session),
            faceit_client=ctx["faceit_client"],
            redis=ctx["redis"],
            arq_pool=None,
        )
        await service._refresh_player_bg(nickname, lock_key)
    logger.info(
        "Фоновое обновление информации о игроке {nickname} завершено.",
        nickname=nickname,
    )


async def task_refresh_stats(ctx, player_id: str, lock_key: str) -> None:
    """Фоновая задача для обновления статистики игрока."""
    logger.info(
        "Начало фонового обновления статистики для игрока {player_id}",
        player_id=player_id,
    )
    session_factory = ctx["session_factory"]

    async with session_factory() as session:
        service = PlayerStatsService(
            stats_repo=PlayerStatsRepository(session),
            faceit_client=ctx["faceit_client"],
            session=session,
            redis=ctx["redis"],
            arq_pool=None,
        )
        await service._refresh_stats_bg(player_id=player_id, lock_key=lock_key)
    logger.info(
        "Фоновое обновление статистики для игрока {player_id} завершено.",
        player_id=player_id,
    )
