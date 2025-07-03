from fastapi import Depends

from repositories.guild import GuildRepository
from repositories.member import MemberRepository
from repositories.role import RoleRepository
from cache.redis_repo import RedisRepository
from cache.redis_instance import redis
from services.guild import GuildService
from services.member import MemberService
from dependencies.repositories import get_guild_repository, get_member_repository, get_role_repository
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
    role_repo: RoleRepository = Depends(get_role_repository)
    ):
    return MemberService(guild_repo, member_repo, role_repo)

def get_request_service(
    guild_repo: GuildRepository = Depends(get_guild_repository),
    member_service: MemberService = Depends(get_member_service),
    role_repo: RoleRepository = Depends(get_role_repository),
    cache: RedisRepository = redis
    ):
    return RequestService(guild_repo, member_service, role_repo, cache)