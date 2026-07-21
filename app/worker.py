"""Модуль фонового воркера ARQ для обработки тяжелых задач."""

import httpx
from loguru import logger
from redis import asyncio as aioredis
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.arq_config import redis_settings
from app.core.config import settings
from app.infrastructure.faceit.client import FaceitClient
from app.infrastructure.db.repositories import (
    PlayerRepository,
    MatchHistoryRepository,
    PlayerStatsRepository,
)
from app.application import MatchHistoryService, PlayerService, PlayerStatsService

db_engine = create_async_engine(
    settings.db.url,
    pool_pre_ping=True,
)
session_factory = async_sessionmaker(
    bind=db_engine,
    expire_on_commit=False,
)


async def startup(ctx: dict) -> None:
    """Инициализация ресурсов при старте."""
    logger.info("Запуск ARQ воркера...")
    limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
    ctx["http_client"] = httpx.AsyncClient(
        base_url=settings.faceit.base_url,
        headers={"Authorization": f"Bearer {settings.faceit.api_key}"},
        limits=limits,
        timeout=httpx.Timeout(10.0, connect=5.0),
        follow_redirects=True,
    )
    ctx["faceit_client"] = FaceitClient(client=ctx["http_client"])
    ctx["redis"] = aioredis.from_url(
        settings.redis.url,
        encoding="utf8",
        decode_responses=False,
    )
    logger.info("Ресурсы воркера успешно инициализированы.")


async def shutdown(ctx: dict) -> None:
    """Вызывается при остановке воркера. Чистит за собой ресурсы."""
    logger.info("Остановка воркера, закрытие соединений...")
    await ctx["http_client"].aclose()
    await ctx["redis"].aclose()
    await db_engine.dispose()
    logger.info("Воркер успешно остановлен.")


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
    async with session_factory() as session:
        match_history_service = MatchHistoryService(
            match_history_repo=MatchHistoryRepository(session),
            player_repo=PlayerRepository(session),
            faceit_client=ctx["faceit_client"],
            session=session,
            redis=ctx["redis"],
            arq_pool=None,
            bg_tasks=None,
        )
        await match_history_service._refresh_match_history_bg(
            player_id,
            limit,
            start_offset,
            lock_key,
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
    async with session_factory() as session:
        service = PlayerService(
            session=session,
            player_repo=PlayerRepository(session),
            faceit_client=ctx["faceit_client"],
            redis=ctx["redis"],
            arq_pool=None,
            bg_tasks=None,
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
    async with session_factory() as session:
        service = PlayerStatsService(
            stats_repo=PlayerStatsRepository(session),
            faceit_client=ctx["faceit_client"],
            session=session,
            redis=ctx["redis"],
            bg_tasks=None,
            arq_pool=None,
        )
        await service._refresh_stats_bg(player_id, lock_key)
    logger.info(
        "Фоновое обновление статистики для игрока {player_id} завершено.",
        player_id=player_id,
    )


class WorkerSettings:
    """Конфигурация, которую считывает CLI команда `arq app.worker.WorkerSettings`."""

    functions = [task_refresh_match_history, task_refresh_player, task_refresh_stats]
    redis_settings = redis_settings
    on_startup = startup
    on_shutdown = shutdown
