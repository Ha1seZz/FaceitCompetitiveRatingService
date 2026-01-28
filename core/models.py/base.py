from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import declared_attr


class Base(DeclarativeBase):
    """
    Базовый класс для всех моделей SQLAlchemy.
    Использует DeclarativeBase (стандарт SQLAlchemy 2.0+).
    """
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"  # Player -> players
