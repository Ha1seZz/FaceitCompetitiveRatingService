from redis import asyncio as aioredis


def get_redis_client() -> aioredis.Redis:
    """Возвращает инициализированный глобальный клиент Redis."""
    from app.main import app

    redis_client = app.state.redis

    if redis_client is None:
        raise RuntimeError("Redis client is not initialized.")
    return redis_client
