"""Конфигурация для ARQ очереди задач."""

from arq.connections import RedisSettings
from app.core.config import settings

redis_settings = RedisSettings(
    host=settings.redis.host,
    port=settings.redis.port,
)


class QueueNames:
    """Имена очередей для разделения задач по приоритетам (если потребуется)."""

    DEFAULT = "arq:queue"
