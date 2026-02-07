"""Инфраструктура БД.

Гарантирует паттерн "один HTTP-запрос -> одна сессия -> один commit/rollback".
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)

from app.core.config import settings


class DatabaseHelper:
    """
    Помощник для работы с асинхронным движком и сессиями SQLAlchemy.
    """

    def __init__(self, url: str, echo: bool = False):
        """Инициализирует асинхронный движок и фабрику сессий."""
        self.engine = create_async_engine(url=url, echo=echo)
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
        )

    async def session_dependency(self) -> AsyncGenerator[AsyncSession, None]:
        """Зависимость (dependency) для FastAPI, предоставляющая новую сессию на каждый запрос."""
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise


# Глобальный экземпляр помощника для использования в приложении
db_helper = DatabaseHelper(
    url=settings.db.url,
    echo=settings.db.echo,
)
