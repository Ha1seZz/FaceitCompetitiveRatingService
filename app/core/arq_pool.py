"""Модуль для создания пула подключений ARQ."""

from arq import create_pool
from arq.connections import ArqRedis
from app.core.arq_config import redis_settings


async def create_arq_pool() -> ArqRedis:
    """Создаёт пул подключений ARQ. Вызывается один раз в lifespan."""
    return await create_pool(redis_settings)
