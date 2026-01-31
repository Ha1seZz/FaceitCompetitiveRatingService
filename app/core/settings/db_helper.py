"""Утилиты для управления подключениями к базе данных."""

from asyncio import current_task
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    async_scoped_session,
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
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    def get_scoped_session(self):
        """Создает сессию, привязанную к текущему контексту задачи asyncio."""
        session = async_scoped_session(
            session_factory=self.session_factory,
            scopefunc=current_task,
        )
        return session

    async def session_dependency(self) -> AsyncGenerator[AsyncSession, None]:
        """Зависимость (dependency) для FastAPI, предоставляющая новую сессию на каждый запрос."""
        async with self.session_factory() as session:
            yield session
            await session.close()

    async def scoped_session_dependency(self) -> AsyncGenerator[AsyncSession, None]:
        """Зависимость для FastAPI, предоставляющая scoped сессию."""
        session = self.get_scoped_session()
        yield session
        await session.remove()


# Глобальный экземпляр помощника для использования в приложении
db_helper = DatabaseHelper(
    url=settings.db.url,
    echo=settings.db.echo,
)
