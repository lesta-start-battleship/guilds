from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from infra.db.database import get_db
from infra.repositories.guild_sql import SQLGuildRepository
from infra.repositories.member_sql import SQLMemberRepository
from infra.repositories.role_sql import SQLRoleRepository

from infra.cache.redis_repo_ import RedisRepository
from infra.cache.redis_instance import redis

def get_guild_repository(session: AsyncSession = Depends(get_db)):
    return SQLGuildRepository(session)

def get_member_repository(session: AsyncSession = Depends(get_db)):
    return SQLMemberRepository(session)

def get_role_repository(session: AsyncSession = Depends(get_db)):
    return SQLRoleRepository(session)

# def get_permission_repository(session: AsyncSession = Depends(get_db)):
#     return PermissionRepository(session)

def get_redis_repository() -> RedisRepository:
    return redis