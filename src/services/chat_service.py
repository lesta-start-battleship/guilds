from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from infra.db.models.guild import MemberORM


async def get_member(session: AsyncSession, user_id: int, guild_id: int) -> MemberORM | None:
    result = await session.execute(
        select(MemberORM)
        .where(MemberORM.user_id == user_id, MemberORM.guild_id == guild_id)
        .options(selectinload(MemberORM.role))
    )
    return result.scalar_one_or_none()