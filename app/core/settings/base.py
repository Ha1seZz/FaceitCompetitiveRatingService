"""Базовая инфраструктура для моделей SQLAlchemy."""

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import declared_attr


class Base(DeclarativeBase):
    """
    Базовый класс для всех моделей SQLAlchemy.

    Использует возможности SQLAlchemy 2.0 для декларативного определения моделей.
    Класс помечен как __abstract__, чтобы SQLAlchemy не пыталась создать для него таблицу.
    """

    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Автоматически генерирует имя таблицы на основе имени класса."""

        return f"{cls.__name__.lower()}s"  # Player -> players
