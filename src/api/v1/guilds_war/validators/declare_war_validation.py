from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, select, func
import uuid

from settings import KafkaTopics
from infra.cache.redis_instance import redis
from infra.db.models.guild import GuildORM
from infra.db.models.guild_war import GuildWarRequest, WarStatus

from ..schemas import DeclareWarRequest
from ..utils import check_guild_owner, advisory_lock_key, send_kafka_message

async def declare_war_validation(
    data: DeclareWarRequest,
    session: AsyncSession,
    request: Request
) -> str:
    
    # 🔐 Advisory Lock для защиты от гонки между двумя гильдиями
    guild_ids = sorted([data.initiator_guild_id, data.target_guild_id])
    lock_key = advisory_lock_key(guild_ids[0], guild_ids[1])
    await session.execute(select(func.pg_advisory_xact_lock(lock_key)))

    # 1. Проверка: существует ли инициирующая гильдия
    result = await session.execute(
        select(GuildORM).where(GuildORM.id == data.initiator_guild_id)
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
        select(GuildORM).where(GuildORM.id == data.target_guild_id)
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


    # #/// УДАЛИТЬ
    # await redis.redis.rpush(f"rage-response:{correlation_id}", "true") #УДАЛИТЬ
    # #///

    # Ждём ответ из Redis

    key = f"rage-response:{correlation_id}"
    rage_response = await redis.redis.blpop(key, timeout=60)

    if not rage_response:
        raise HTTPException(504, "Timeout while validating rage points")

    _, value = rage_response
    if value.decode("utf-8") != "true":
        raise HTTPException(400, "Not enough rage points to declare war")
    
    # await redis.redis.delete(key) /// нельзя тут удалять (только когда status: fininshed cancled declined expired)

    return correlation_id 