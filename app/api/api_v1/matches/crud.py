from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.match import Match
from .schemas import MatchCreate


async def create_or_update_match(
    session: AsyncSession,
    match_in: dict,
) -> Match:
    """
    Создает новый матч или обновляет существующий на основе данных из Faceit API.
    """
    # Отсекает лишние поля и преобразует в словарь
    validated_data = MatchCreate(**match_in)
    match_data = validated_data.model_dump()

    stmt = select(Match).where(Match.match_id == match_data.get("match_id", ""))
    result = await session.execute(stmt)
    db_match = result.scalar_one_or_none()

    if db_match:  # if match exists - update
        for key, value in match_data.items():
            setattr(db_match, key, value)
    else:  # if match not exists - create
        db_match = Match(**match_data)
        session.add(db_match)

    await session.commit()
    await session.refresh(db_match)
    return db_match
