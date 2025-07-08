from typing import List

from domain.entities.guild_request import GuildJoinRequest
from domain.exceptions.guild import GuildIsFullException
from domain.exceptions.guild_request import RequestAlreadyExistException, RequestNotFoundException
from domain.exceptions.member import MemberAlreadyInGuildException, MemberInOtherGuildException, MemberNotFoundException, MemberNotHavePermissionException
from domain.repositories.member_repo import MemberRepositoryBase
from domain.repositories.role_repo import RoleRepositoryBase
from domain.values.permission import Permission
from domain.repositories.cache_repo import CacheRepositoryBase
from domain.values.tag import Tag

from services.converters.domain_to_dto import request_domain_to_dto
from services.guild_ import GuildService

from schemas.guild_request import RequestResponse
from schemas.member import MemberResponse

class RequestService:
    def __init__(
        self,
        guild_service: GuildService,
        member_repo: MemberRepositoryBase,
        role_repo: RoleRepositoryBase,
        cache: CacheRepositoryBase
        ):
        self.guild_service = guild_service
        self.member_repo = member_repo
        self.role_repo = role_repo
        self.cache = cache
        
    
    async def validate_guild_member(self, tag: str, user_id: int):
        await self.guild_service.get_by_tag(tag)
        
        guild_member = await self.member_repo.get_by_id(user_id)
        if not guild_member:
            raise MemberNotFoundException(user_id)
        
        if str(guild_member.guild_tag) != tag:
            raise MemberInOtherGuildException(user_id)
        
        if not Permission.invite_members in guild_member.role.permissions:
            raise MemberNotHavePermissionException(user_id)
    
    
    async def get_requests_by_guild_tag(self, tag: str, user_id: int) -> List[RequestResponse]:
        await self.validate_guild_member(tag, user_id)
        requests = await self.cache.request_list_by_tag(tag)
        return [request_domain_to_dto(r) for r in requests]
    
    
    async def add_request(self, tag: str, user_id: int, user_name: str) -> RequestResponse:
        guild = await self.guild_service.get_by_tag(tag)
        if guild.is_full:
            raise GuildIsFullException(guild.tag)
        
        member = await self.member_repo.get_by_id(user_id)
        if member:
            raise MemberAlreadyInGuildException(user_id)
        
        if await self.cache.check_request(tag, user_id):
            raise RequestAlreadyExistException(tag)
        
        req = GuildJoinRequest(
            guild_tag=Tag(tag),
            user_id=user_id,
            username=user_name,
            created_at=None,
            status='pending'
        )
        req = await self.cache.create(req)
        return request_domain_to_dto(req) if req else None
    
    
    async def cancel_request(self, tag: str, guild_user_id: int, user_id: int) -> None:
        await self.validate_guild_member(tag, guild_user_id)
        
        if not await self.cache.check_request(tag, user_id):
            raise RequestNotFoundException(tag)
        
        await self.cache.delete(tag, user_id)
    
    
    async def apply_request(self, tag: str, guild_user_id: int, user_id: int) -> MemberResponse:
        await self.validate_guild_member(tag, guild_user_id)
        if not await self.cache.check_request(tag, user_id):
            raise RequestNotFoundException(tag)
        req = await self.cache.get_request(tag, user_id)
        member = await self.guild_service.add_member(str(req.guild_tag), guild_user_id, req.user_id, req.username)
        await self.cache.delete(tag, user_id)
        return member
    
    
    async def on_guild_deleted(self, guild_tag: str) -> bool:
        await self.cache.request_list_delete_by_guild_tag(guild_tag)
    
    
    async def on_user_deleted(self, user_id: int) -> bool:
        await self.cache.request_list_delete_by_user_id(user_id)
    
    
    async def on_username_changed(self, user_id: int, username: str) -> bool:
        requests = await self.cache.request_list_by_user_id(user_id)
        for req in requests:
            req.username = username
            await self.cache.save(req)