from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models.guild import Member


async def get_member(session: AsyncSession, user_id: int, guild_id: int) -> Member | None:
    result = await session.execute(
        select(Member)
        .where(Member.user_id == user_id, Member.guild_id == guild_id)
        .options(selectinload(Member.role))
    )
    return result.scalar_one_or_none()