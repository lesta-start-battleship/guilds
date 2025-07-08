from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, select, func
from datetime import datetime, timezone
from sqlalchemy.exc import DBAPIError
from asyncpg.exceptions import DeadlockDetectedError
import asyncio

import uuid
import json
from aiokafka import AIOKafkaProducer

from settings import KafkaTopics
from cache.redis_instance import redis
from db.models.guild import Guild
from db.models.guild_war import GuildWarRequest, WarStatus
from db.database import get_db


from .schemas import DeclareWarRequest, DeclareWarResponse
from .utils import check_guild_owner, advisory_lock_key, send_kafka_message

router = APIRouter()
# http_bearer = HTTPBearer()


@router.post("/declare", response_model=DeclareWarResponse)
async def declare_war(
    data: DeclareWarRequest,
    request: Request, 
    session: AsyncSession = Depends(get_db),
    # token: HTTPAuthorizationCredentials = Depends(http_bearer),
):
    try:

        try:
            pong = await redis.ping()
            if not pong:
                raise HTTPException(500, detail="Redis is not available")
        except Exception as e:
            raise HTTPException(500, detail=f"Redis connection failed: {e}")

        # Отправка сообщения в Kafka
        correlation_id = str(uuid.uuid4())
        message = {
            "initiator_guild_id": data.initiator_guild_id,
            "initiator_owner_id": data.initiator_owner_id,
            "correlation_id": correlation_id
        }
        
        await send_kafka_message(
            request=request,
            topic=KafkaTopics.initiator_guild_wants_declare_war,
            message=message,
        )


        # 2. Ждём ответ из Redis
    
        key = f"rage-response:{correlation_id}"
        rage_response = await redis.redis.blpop(key, timeout=60)

        if not rage_response:
            raise HTTPException(504, "Timeout while validating rage points")

        _, value = rage_response
        if value.decode("utf-8") != "true":
            raise HTTPException(400, "Not enough rage points to declare war")
        
        await redis.redis.delete(key)
        

        async with session.begin():  # Обеспечивает транзакционность

            # 🔐 Advisory Lock для защиты от гонки между двумя гильдиями
            guild_ids = sorted([data.initiator_guild_id, data.target_guild_id])
            lock_key = advisory_lock_key(guild_ids[0], guild_ids[1])
            await session.execute(select(func.pg_advisory_xact_lock(lock_key)))

            # 1. Проверка: существует ли инициирующая гильдия
            result = await session.execute(
                select(Guild).where(Guild.id == data.initiator_guild_id)
            )
            initiator_guild = result.scalar_one_or_none()
            if not initiator_guild:
                raise HTTPException(status_code=404, detail="Initiator guild not found")

            # 2. Проверка: пользователь — владелец этой гильдии
            await check_guild_owner(
                session=session,
                user_id=data.initiator_owner_id,
                guild_id=data.initiator_guild_id
            )

            # 3. Проверка: существует ли целевая гильдия
            result = await session.execute(
                select(Guild).where(Guild.id == data.target_guild_id)
            )
            target_guild = result.scalar_one_or_none()
            if not target_guild:
                raise HTTPException(status_code=404, detail="Target guild not found")

            # 4. Самой себе — нельзя
            if data.initiator_guild_id == data.target_guild_id:
                raise HTTPException(status_code=400, detail="Guild cannot declare war on itself")

            # 5. Проверка: нет уже активной/ожидающей войны между ними
            result = await session.execute(
                select(GuildWarRequest).where(
                    GuildWarRequest.status.in_([WarStatus.pending, WarStatus.active]),
                    or_(
                        and_(
                            GuildWarRequest.initiator_guild_id == data.initiator_guild_id,
                            GuildWarRequest.target_guild_id == data.target_guild_id
                        ),
                        and_(
                            GuildWarRequest.initiator_guild_id == data.target_guild_id,
                            GuildWarRequest.target_guild_id == data.initiator_guild_id
                        )
                    )
                )
            )
            existing = result.scalar_one_or_none()
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail="A war request between these guilds already exists"
                )

            # 6. Инициатор не может участвовать в другой войне
            result = await session.execute(
                select(GuildWarRequest).where(
                    GuildWarRequest.status.in_([WarStatus.pending, WarStatus.active]),
                    GuildWarRequest.initiator_guild_id == data.initiator_guild_id
                )
            )
            conflict = result.scalar_one_or_none()
            if conflict:
                raise HTTPException(
                    status_code=400,
                    detail="Your guild is already initiating another war"
                )

            # 7. Целевая гильдия не может быть в active-войне
            result = await session.execute(
                select(GuildWarRequest).where(
                    GuildWarRequest.status == WarStatus.active,
                    or_(
                        GuildWarRequest.initiator_guild_id == data.target_guild_id,
                        GuildWarRequest.target_guild_id == data.target_guild_id
                    )
                )
            )
            target_conflict = result.scalar_one_or_none()
            if target_conflict:
                raise HTTPException(
                    status_code=400,
                    detail="Target guild is already participating in an active war"
                )
            
            # 8. Создаём заявку
            new_request = GuildWarRequest(
                initiator_guild_id=data.initiator_guild_id,
                target_guild_id=data.target_guild_id,
                status=WarStatus.pending,
                created_at=datetime.now(timezone.utc)
            )
            session.add(new_request)
            await session.flush()

            war_id = new_request.id
            await redis.redis.set(f"war-correlation:{war_id}", correlation_id)

            response =  DeclareWarResponse(
                war_id=new_request.id,
                initiator_guild_id=new_request.initiator_guild_id,
                target_guild_id=new_request.target_guild_id,
                status=new_request.status,
                created_at=new_request.created_at,
            )
        
        # Отправка в Kafka
        await send_kafka_message(
            request=request,
            topic=KafkaTopics.guild_war_declare,
            message=response,
        )

        return response
    
    except DBAPIError as e:
        if isinstance(e.__cause__, DeadlockDetectedError):
            raise HTTPException(409, detail="Conflict due to concurrent request (deadlock)")
        raise