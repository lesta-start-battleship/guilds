from fastapi import Depends

from domain.repositories.guild_repo import GuildRepositoryBase
from domain.repositories.member_repo import MemberRepositoryBase
from domain.repositories.role_repo import RoleRepositoryBase
from domain.repositories.cache_repo import CacheRepositoryBase

from dependencies.repositories import get_guild_repository, get_member_repository, get_redis_repository, get_role_repository

from services.guild_ import GuildService
from services.member_ import MemberService
from services.guild_request_ import RequestService


def get_guild_service(
    guild_repo: GuildRepositoryBase = Depends(get_guild_repository),
    member_repo: MemberRepositoryBase = Depends(get_member_repository),
    role_repo: RoleRepositoryBase = Depends(get_role_repository)
    ):
    return GuildService(guild_repo, member_repo, role_repo)

def get_member_service(
    member_repo: MemberRepositoryBase = Depends(get_member_repository)
    ):
    return MemberService(member_repo)

def get_request_service(
    guild_service: GuildService = Depends(get_guild_service),
    member_repo: MemberRepositoryBase = Depends(get_member_repository),
    role_repo: RoleRepositoryBase = Depends(get_role_repository),
    cache: CacheRepositoryBase = Depends(get_redis_repository)
    ):
    return RequestService(guild_service, member_repo, role_repo, cache)