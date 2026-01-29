from asyncio import current_task

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    async_scoped_session,
)

from app.core.config import settings


class DatabaseHelper:
    """
    Класс-помощник для управления подключением к БД и сессиями.
    Инкапсулирует создание движка (engine) и фабрики сессий.
    """

    def __init__(self, url: str, echo: bool = False):
        self.engine = create_async_engine(url=url, echo=echo)  # Асинхронный движок
        self.session_factory = async_sessionmaker(  # Фабрика сессий
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    def get_scoped_session(self):
        """Создает сессию, ограниченную текущей задачей asyncio (current_task)."""
        session = async_scoped_session(
            session_factory=self.session_factory,
            scopefunc=current_task,
        )
        return session

    async def session_dependency(self) -> AsyncSession:  # type: ignore
        """Генератор сессий для FastAPI Depends."""
        async with self.session_factory() as session:
            yield session
            await session.close()

    async def scoped_session_dependency(self) -> AsyncSession:  # type: ignore
        """Альтернативный генератор для использования scoped сессий."""
        session = self.get_scoped_session()
        yield session
        await session.remove()


db_helper = DatabaseHelper(
    url=settings.db.url,
    echo=settings.db.echo,
)
