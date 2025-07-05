from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from repositories.guild import GuildRepository
from repositories.member import MemberRepository
from repositories.role import RoleRepository
from repositories.permisson import PermissionRepository

from cache.redis_repo import RedisRepository
from cache.redis_instance import redis

def get_guild_repository(session: AsyncSession = Depends(get_db)):
    return GuildRepository(session)

def get_member_repository(session: AsyncSession = Depends(get_db)):
    return MemberRepository(session)

def get_role_repository(session: AsyncSession = Depends(get_db)):
    return RoleRepository(session)

def get_permission_repository(session: AsyncSession = Depends(get_db)):
    return PermissionRepository(session)

def get_redis_repository() -> RedisRepository:
    return redis