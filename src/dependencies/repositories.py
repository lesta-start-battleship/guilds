from aiokafka import AIOKafkaProducer
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from infra.broker.producer import KafkaPublisher
from infra.db.database import get_db
from infra.repositories.guild_sql import SQLGuildRepository
from infra.repositories.member_sql import SQLMemberRepository
from infra.repositories.role_sql import SQLRoleRepository

from infra.cache.redis_repo_ import RedisRepository
from infra.cache.redis_instance import redis

from settings import settings

producer_instance = None

async def init_producer():
    global producer_instance
    producer_instance = AIOKafkaProducer(bootstrap_servers=settings.kafka_service)
    await producer_instance.start()

def get_producer():
    if not producer_instance:
        raise RuntimeError('Producer not initialized')
    return producer_instance

def get_guild_repository(session: AsyncSession = Depends(get_db)):
    return SQLGuildRepository(session)

def get_member_repository(session: AsyncSession = Depends(get_db)):
    return SQLMemberRepository(session)

def get_role_repository(session: AsyncSession = Depends(get_db)):
    return SQLRoleRepository(session)

def get_redis_repository() -> RedisRepository:
    return redis

def get_producer_():
    return KafkaPublisher(get_producer())