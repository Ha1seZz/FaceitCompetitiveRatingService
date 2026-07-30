"""Модуль фонового воркера ARQ для обработки тяжелых задач."""

import httpx
from loguru import logger
from redis import asyncio as aioredis
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.arq_config import redis_settings
from app.core.config import settings
from app.infrastructure.faceit.client import FaceitClient
from app.tasks import (
    task_refresh_match_history,
    task_refresh_player,
    task_refresh_stats,
)


async def startup(ctx: dict) -> None:
    """Инициализация ресурсов при старте."""
    logger.info("Запуск ARQ воркера...")

    db_engine = create_async_engine(settings.db.url, pool_pre_ping=True)
    ctx["db_engine"] = db_engine

    session_factory = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    ctx["session_factory"] = session_factory

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
    await ctx["db_engine"].dispose()
    logger.info("Воркер успешно остановлен.")


class WorkerSettings:
    """Конфигурация, которую считывает CLI команда `arq app.worker.WorkerSettings`."""

    functions = [task_refresh_match_history, task_refresh_player, task_refresh_stats]
    redis_settings = redis_settings
    on_startup = startup
    on_shutdown = shutdown
