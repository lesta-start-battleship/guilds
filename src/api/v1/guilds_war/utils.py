from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, Request, status

import hashlib

import asyncio
import json
from typing import Union

from aiokafka import AIOKafkaProducer
from pydantic import BaseModel

from infra.db.models.guild import GuildORM


async def check_guild_owner(
    session: AsyncSession,
    user_id: int,
    guild_id: int
) -> None:
    result = await session.execute(
        select(GuildORM.owner_id).where(GuildORM.id == guild_id)
    )
    owner_id = result.scalar_one_or_none()

    if owner_id is None:
        raise HTTPException(status_code=404, detail="Guild not found")

    if owner_id != user_id:
        raise HTTPException(status_code=403, detail="Only the guild owner can perform this action")


    

def advisory_lock_key(guild1_id: int, guild2_id: int) -> int:
    # Сортируем внутри функции
    pair_str = f"{min(guild1_id, guild2_id)}:{max(guild1_id, guild2_id)}"
    digest = hashlib.sha256(pair_str.encode('utf-8')).digest()
    lock_key = int.from_bytes(digest[:8], byteorder='big', signed=False)
    return lock_key % (2**63)



async def get_guild_owner(session: AsyncSession, guild_id: int) -> int:

    #Получает owner_id гильдии по её ID.

    result = await session.execute(
        select(GuildORM.owner_id).where(GuildORM.id == guild_id)
    )
    owner_id = result.scalar_one_or_none()
    if owner_id is None:
        raise HTTPException(404, detail=f"Guild with id {guild_id} not found")

    return owner_id




async def send_kafka_message(
    request: Request,
    topic: str,
    message: Union[BaseModel, dict],
    timeout: int = 10,
):
    """
    Отправляет сообщение в Kafka-топик с использованием producer из request.app.state.

    :param request: FastAPI Request (с доступом к app.state.producer)
    :param topic: Название Kafka-топика
    :param message: Pydantic-модель или словарь
    :param timeout: Таймаут отправки
    """
    try:
        if isinstance(message, BaseModel):
            encoded = message.model_dump_json().encode("utf-8")
        elif isinstance(message, dict):
            encoded = json.dumps(message).encode("utf-8")
        else:
            raise ValueError("Message must be a Pydantic model or a dict")

        producer: AIOKafkaProducer = request.app.state.producer

        await asyncio.wait_for(
            producer.send_and_wait(topic, encoded),
            timeout=timeout
        )
    except Exception as e:
        print(f"[Kafka ERROR] {type(e).__name__}: {e}")


