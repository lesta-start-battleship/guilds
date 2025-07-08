from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timezone
from sqlalchemy.exc import DBAPIError
from asyncpg.exceptions import DeadlockDetectedError

from infra.db.models.guild_war import GuildWarRequest, WarStatus, GuildWarRequestHistory
from infra.db.database import get_db

from .schemas import CancelWarRequest, CancelWarResponse
from .utils import check_guild_owner, advisory_lock_key

router = APIRouter()


@router.post("/cancel/{request_id}", response_model=CancelWarResponse)
async def cancel_war(
    data: CancelWarRequest,
    request_id: int = Path(..., description="ID заявки на войну"),
    session: AsyncSession = Depends(get_db)
):
    try:
        async with session.begin():
            result = await session.execute(
                select(GuildWarRequest)
                .where(GuildWarRequest.id == request_id)
                .with_for_update()
            )
            war_request = result.scalar_one_or_none()
            if not war_request:
                raise HTTPException(404, detail="Request not found")

            if war_request.status != WarStatus.pending:
                raise HTTPException(400, detail="Only pending requests can be canceled")

            # Advisory lock
            guild_ids = sorted([war_request.initiator_guild_id, war_request.target_guild_id])
            lock_key = advisory_lock_key(guild_ids[0], guild_ids[1])
            await session.execute(select(func.pg_advisory_xact_lock(lock_key)))
            
            # Проверка владельца одной из гильдий
            try:
                await check_guild_owner(session, data.user_id, war_request.initiator_guild_id)
            except HTTPException:
                try:
                    await check_guild_owner(session, data.user_id, war_request.target_guild_id)
                except HTTPException:
                    raise HTTPException(403, detail="User is not an owner of either guild")

            # Перенос в историю
            now = datetime.now(timezone.utc)
            session.add(GuildWarRequestHistory(
                request_id=war_request.id,
                initiator_guild_id=war_request.initiator_guild_id,
                target_guild_id=war_request.target_guild_id,
                status=WarStatus.canceled,
                created_at=war_request.created_at,
                finished_at=now
            ))
            await session.delete(war_request)

        return CancelWarResponse(
                request_id=request_id,
                status=WarStatus.canceled,
                cancelled_by=data.user_id,
                cancelled_at=now
        )

    except DBAPIError as e:
        if isinstance(e.__cause__, DeadlockDetectedError):
            raise HTTPException(409, detail="Conflict due to concurrent request (deadlock)")
        raise