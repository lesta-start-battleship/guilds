from fastapi import Depends

from repositories.guild import GuildRepository
from repositories.member import MemberRepository
from repositories.role import RoleRepository
from repositories.permisson import PermissionRepository

from dependencies.repositories import get_guild_repository, get_member_repository, get_redis_repository, get_role_repository, get_permission_repository

from cache.redis_repo import RedisRepository
from cache.redis_instance import redis

from services.guild import GuildService
from services.member import MemberService
from services.guild_request import RequestService


def get_guild_service(
    guild_repo: GuildRepository = Depends(get_guild_repository),
    member_repo: MemberRepository = Depends(get_member_repository),
    role_repo: RoleRepository = Depends(get_role_repository)
    ):
    return GuildService(guild_repo, member_repo, role_repo)

def get_member_service(
    guild_repo: GuildRepository = Depends(get_guild_repository),
    member_repo: MemberRepository = Depends(get_member_repository),
    role_repo: RoleRepository = Depends(get_role_repository),
    permission_repo: PermissionRepository = Depends(get_permission_repository),
    ):
    return MemberService(guild_repo, member_repo, role_repo, permission_repo)

def get_request_service(
    guild_repo: GuildRepository = Depends(get_guild_repository),
    member_service: MemberService = Depends(get_member_service),
    role_repo: RoleRepository = Depends(get_role_repository),
    permission_repo: PermissionRepository = Depends(get_permission_repository),
    cache: RedisRepository = Depends(get_redis_repository)
    ):
    return RequestService(guild_repo, member_service, role_repo, permission_repo, cache)