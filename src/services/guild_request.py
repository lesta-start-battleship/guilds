from typing import List

from repositories.guild import GuildRepository
from repositories.role import RoleRepository

from db.models.guild import EnumPermissions

from exceptions.guild import UncorrectGuildTagException, GuildNotFoundException
from exceptions.member import MemberAlreadyInGuildException, MemberNotFoundException, MemberNotHavePermissionException
from exceptions.guild_request import RequestAlreadyExistException, RequestNotFoundException

from services.converters import cache_to_dto
from services.member import MemberService
from cache.redis_repo import RedisRepository
from utils.string_validator import validate_str

from schemas.requests_invites import RequestResponse
from schemas.member import AddMemberRequest, MemberResponse

class RequestService:
    def __init__(
        self,
        guild_repo: GuildRepository,
        member_service: MemberService,
        role_repo: RoleRepository,
        cache: RedisRepository
        ):
        self.guild_repo = guild_repo
        self.member_service = member_service
        self.role_repo = role_repo
        self.cache = cache
        
    
    async def validate_guild_member(self, tag: str, user_id: int):
        if not validate_str(tag):
            raise UncorrectGuildTagException
        
        guild = await self.guild_repo.get_by_tag(tag)
        if not guild:
            raise GuildNotFoundException
            
        member = await self.member_service.get_user_by_id(user_id)
        if not member:
            raise MemberNotFoundException
        
        if member.guild_tag != tag or user_id != guild.owner_id or \
        not self.permission_repo.get_by_title(EnumPermissions.invite_members) in member.role.permissions:
            raise MemberNotHavePermissionException
    
    
    async def get_requests_by_guild_tag(self, tag: str, user_id: int) -> List[RequestResponse]:
        self.validate_guild_member(tag, user_id)
        requests = await self.cache.get_requests(tag)
        return [cache_to_dto(r) for r in requests]
    
    
    async def add_request(self, tag: str, user_id: int) -> None:
        try:
            member = await self.member_service.get_user_by_id(user_id)
        except MemberNotFoundException:
            pass
        if member:
            raise MemberAlreadyInGuildException
        
        if not validate_str(tag):
            raise UncorrectGuildTagException
        
        guild = await self.guild_repo.get_by_tag(tag)
        if not guild:
            raise GuildNotFoundException
        
        if await self.cache.check_request(tag, user_id):
            RequestAlreadyExistException
        
        await self.cache.add_request(tag, user_id)
    
    
    async def cancel_request(self, tag: str, guild_user_id: int, user_id: int) -> None:
        self.validate_guild_member(tag, guild_user_id)
        
        if not await self.cache.check_request(tag, user_id):
            RequestNotFoundException
        
        try:
            member = await self.member_service.get_user_by_id(user_id)
        except MemberNotFoundException:
            pass
        if member:
            raise MemberAlreadyInGuildException
        
        await self.cache.remove_request(tag, user_id)
    
    
    async def apply_request(self, tag: str, guild_user_id: int, user_id: int) -> MemberResponse:
        self.validate_guild_member(tag, guild_user_id)
        
        if not await self.cache.check_request(tag, user_id):
            RequestNotFoundException
        
        try:
            member = await self.member_service.get_user_by_id(user_id)
        except MemberNotFoundException:
            pass
        if member:
            raise MemberAlreadyInGuildException
        
        await self.cache.remove_request(tag, user_id)
        
        self.member_service.add_member(tag, guild_user_id, AddMemberRequest(user_id))