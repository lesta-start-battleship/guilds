from fastapi import APIRouter, Depends, HTTPException, Path, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timezone
from sqlalchemy.exc import DBAPIError
from asyncpg.exceptions import DeadlockDetectedError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from settings import KafkaTopics
from cache.redis_instance import redis

from db.models.guild_war import GuildWarRequest, WarStatus, GuildWarRequestHistory
from db.database import get_db

from .schemas import CancelWarRequest, CancelWarResponse, CancelWarMessage
from .utils import check_guild_owner, advisory_lock_key, send_kafka_message, get_guild_owner, check_user_access

router = APIRouter()
http_bearer = HTTPBearer()

@router.post("/cancel/{war_id}", response_model=CancelWarResponse)
async def cancel_war(
    data: CancelWarRequest,
    request: Request,
    war_id: int = Path(..., description="ID заявки на войну"),
    session: AsyncSession = Depends(get_db),
    token: HTTPAuthorizationCredentials = Depends(http_bearer),
):
    try:
        payload = await check_user_access(token)
         
        async with session.begin():
            result = await session.execute(
                select(GuildWarRequest)
                .where(GuildWarRequest.id == war_id)
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
                await check_guild_owner(session, data.owner_id, war_request.initiator_guild_id)
            except HTTPException:
                try:
                    await check_guild_owner(session, data.owner_id, war_request.target_guild_id)
                except HTTPException:
                    raise HTTPException(403, detail="User is not an owner of either guild")

            # Перенос в историю
            now = datetime.now(timezone.utc)
            session.add(GuildWarRequestHistory(
                war_id=war_request.id,
                initiator_guild_id=war_request.initiator_guild_id,
                target_guild_id=war_request.target_guild_id,
                status=WarStatus.canceled,
                created_at=war_request.created_at,
                finished_at=now
            ))
            await session.delete(war_request)

            initiator_owner_id = await get_guild_owner(session, war_request.initiator_guild_id)
            target_owner_id = await get_guild_owner(session, war_request.target_guild_id)


            correlation_id = await redis.redis.get(f"war-correlation:{war_id}")
            if correlation_id:
                correlation_id = correlation_id.decode("utf-8")  # bytes → str
                await redis.redis.delete(f"war-correlation:{war_id}")
            else:
                print(f"[WARN] Correlation ID not found for war_id={war_id}")

            message = CancelWarMessage(
                    war_id=war_id,
                    status=WarStatus.canceled,
                    cancelled_by=data.owner_id,
                    cancelled_at=now,
                    initiator_guild_id=war_request.initiator_guild_id,
                    target_guild_id=war_request.target_guild_id,
                    initiator_owner_id=initiator_owner_id,
                    target_owner_id=target_owner_id,
                    correlation_id=str(correlation_id)
            )

            await send_kafka_message(
                request=request,
                topic=KafkaTopics.guild_war_canceled_declined_expired,
                message=message,
            )

        return CancelWarResponse(
                    war_id=war_id,
                    status=WarStatus.canceled,
                    cancelled_by=data.owner_id,
                    cancelled_at=now,
                    initiator_guild_id=war_request.initiator_guild_id,
                    target_guild_id=war_request.target_guild_id,
                    initiator_owner_id=initiator_owner_id,
                    target_owner_id=target_owner_id,
            )

    except DBAPIError as e:
        if isinstance(e.__cause__, DeadlockDetectedError):
            raise HTTPException(409, detail="Conflict due to concurrent request (deadlock)")
        raise