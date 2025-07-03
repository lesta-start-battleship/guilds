from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
import hashlib

from db.models.guild import Member, Role

async def check_guild_owner(
    session: AsyncSession,
    user_id: int,
    guild_id: int
) -> None:
    result = await session.execute(
        select(Member)
        .join(Role)
        .where(
            Member.user_id == user_id,
            Member.guild_id == guild_id,
            Role.owner == True
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="Only the guild owner can perform this action")
    

def advisory_lock_key(guild1_id: int, guild2_id: int) -> int:
    # Сортируем внутри функции
    pair_str = f"{min(guild1_id, guild2_id)}:{max(guild1_id, guild2_id)}"
    digest = hashlib.sha256(pair_str.encode('utf-8')).digest()
    lock_key = int.from_bytes(digest[:8], byteorder='big', signed=False)
    return lock_key % (2**63)