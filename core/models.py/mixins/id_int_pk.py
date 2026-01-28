from sqlalchemy.orm import Mapped, mapped_column

class IdIntPkMixin:
    """Миксин для добавления целочисленного первичного ключа."""
    id: Mapped[int] = mapped_column(primary_key=True)
