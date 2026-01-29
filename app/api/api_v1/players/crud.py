from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.player import Player
from .schemas import PlayerCreate


async def create_or_update_player(
    session: AsyncSession,
    player_in: dict,
) -> Player:
    """
    Создает нового игрока или обновляет существующего на основе данных из Faceit API.
    """
    # Отсекает лишние поля и преобразует в словарь
    validated_data = PlayerCreate(**player_in)
    player_data = validated_data.model_dump()

    stmt = select(Player).where(Player.player_id == player_data.get("player_id", ""))
    result = await session.execute(stmt)
    db_player = result.scalar_one_or_none()

    if db_player:  # if player exists - update
        for key, value in player_data.items():
            setattr(db_player, key, value)
    else:  # if player not exists - create
        db_player = Player(**player_data)
        session.add(db_player)

    await session.commit()
    await session.refresh(db_player)
    return db_player
