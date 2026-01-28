from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import declared_attr

from core.config import settings


class Base(DeclarativeBase):
    """
    Базовый класс для всех моделей SQLAlchemy.
    Использует DeclarativeBase (стандарт SQLAlchemy 2.0+).
    """
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"  # Player -> players
