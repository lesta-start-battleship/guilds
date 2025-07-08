from fastapi import APIRouter, Depends, HTTPException, Path, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, select, func
from datetime import datetime, timezone
from sqlalchemy.exc import DBAPIError
from asyncpg.exceptions import DeadlockDetectedError
from aiokafka import AIOKafkaProducer
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from cache.redis_instance import redis

from settings import KafkaTopics
from db.models.guild_war import GuildWarRequest, WarStatus, GuildWarRequestHistory
from db.database import get_db

from ..schemas import ConfirmWarRequest, ConfirmWarResponse, DeclinedWarMessage, ConfirmWarMessage
from ..utils import check_guild_owner, advisory_lock_key, get_guild_owner, send_kafka_message, check_user_access


async def delete_conflict_request(
    data: ConfirmWarRequest,
    war_request: GuildWarRequest,
    war_id: int, 
    updated_at: datetime,
    session: AsyncSession,
    request: Request
):
    
      # 5. Найти и удалить конфликтующие pending-заявки
    result = await session.execute(
        select(GuildWarRequest).where(
            GuildWarRequest.status == WarStatus.pending,
            GuildWarRequest.id != war_id,
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

    conflicting_requests = result.scalars().all()

    for req in conflicting_requests:
        session.add(GuildWarRequestHistory(
            war_id=req.id,
            initiator_guild_id=req.initiator_guild_id,
            target_guild_id=req.target_guild_id,
            status=WarStatus.declined,
            created_at=req.created_at,
            finished_at=updated_at
        ))
        await session.delete(req)
        
        req_initiator_owner_id = await get_guild_owner(session, req.initiator_guild_id)

        correlation_id = await redis.redis.get(f"war-correlation:{req.id}")
        if correlation_id:
            correlation_id = correlation_id.decode("utf-8")  # bytes → str
            await redis.redis.delete(f"war-correlation:{req.id}")
        else:
            print(f"[WARN] Correlation ID not found for war_id={req.id}")

        # Отправка в Kafka
        msg = DeclinedWarMessage(
            war_id=req.id,
            status=WarStatus.declined.value,
            initiator_guild_id=req.initiator_guild_id,
            target_guild_id=req.target_guild_id,
            initiator_owner_id=req_initiator_owner_id,
            target_owner_id=data.target_owner_id,
            declined_at=updated_at,
            correlation_id=correlation_id
        )

        await send_kafka_message(
            request=request,
            topic=KafkaTopics.guild_war_canceled_declined_expired,
            message=msg,
        )