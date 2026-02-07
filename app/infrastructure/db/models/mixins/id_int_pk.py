"""Миксин для добавления первичного ключа типа Integer."""

from sqlalchemy.orm import Mapped, mapped_column


class IdIntPkMixin:
    """Добавляет автоинкрементный int первичный ключ `id`."""
    id: Mapped[int] = mapped_column(primary_key=True)
