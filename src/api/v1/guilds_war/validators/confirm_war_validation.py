from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, select, func
from infra.db.models.guild_war import GuildWarRequest, WarStatus

from ..schemas import ConfirmWarRequest
from ..utils import check_guild_owner, advisory_lock_key


async def confirm_war_validation(
    data: ConfirmWarRequest,
    war_id: int, 
    session: AsyncSession,
)-> GuildWarRequest:
    
    # 1. Найти заявку
    result = await session.execute(
        select(GuildWarRequest).where(GuildWarRequest.id == war_id).with_for_update()
    )

    war_request = result.scalar_one_or_none()
    if not war_request:
        raise HTTPException(404, detail="Request not found")
    

    if war_request.status != WarStatus.pending:
        raise HTTPException(400, detail="Request is not pending")

    # 🔐 Advisory lock через SQLAlchemy func
    guild_ids = sorted([war_request.initiator_guild_id, war_request.target_guild_id])
    lock_key = advisory_lock_key(guild_ids[0], guild_ids[1])
    await session.execute(select(func.pg_advisory_xact_lock(lock_key)))

    # 2. Проверка: владелец целевой гильдии
    await check_guild_owner(
        session=session,
        user_id=data.target_owner_id,
        guild_id=war_request.target_guild_id
    )

    # 3. Проверка: гильдии не участвуют уже в active войне
    result = await session.execute(
        select(GuildWarRequest).where(
            GuildWarRequest.status == WarStatus.active,
            GuildWarRequest.id != war_request.id,
            or_(
                GuildWarRequest.initiator_guild_id.in_([
                    war_request.initiator_guild_id, war_request.target_guild_id
                ]),
                GuildWarRequest.target_guild_id.in_([
                    war_request.initiator_guild_id, war_request.target_guild_id
                ])
            )
        )
    )

    if result.scalar_one_or_none():
        raise HTTPException(400, detail="One of the guilds is already in an active war")

    return war_request