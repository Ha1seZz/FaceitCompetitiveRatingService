from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.player import Player
from .schemas import PlayerCreate


async def create_or_update_player(
    session: AsyncSession,
    player_in: PlayerCreate,
) -> Player:
    stmt = select(Player).where(Player.player_id == player_in.player_id)
    result = await session.execute(stmt)
    db_player = result.scalar_one_or_none()

    player_data = player_in.model_dump()

    if db_player:  # if exists - update
        for key, value in player_data.items():
            setattr(db_player, key, value)
    else:  # if not exists - create
        db_player = Player(**player_data)
        session.add(db_player)

    await session.commit()
    await session.refresh()
    return db_player
