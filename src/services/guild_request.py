from typing import List

from repositories.guild import GuildRepository
from repositories.role import RoleRepository
from repositories.permisson import PermissionRepository

from db.models.guild import EnumPermissions

from exceptions.guild import GuildIsFullException, UncorrectGuildTagException, GuildNotFoundException
from exceptions.member import MemberAlreadyInGuildException, MemberNotFoundException, MemberNotHavePermissionException
from exceptions.guild_request import RequestAlreadyExistException, RequestNotFoundException

from services.converters import cache_to_dto
from services.member import MemberService
from cache.redis_repo import RedisRepository
from utils.string_validator import validate_str

from schemas.guild_request import RequestResponse
from schemas.member import AddMemberRequest, MemberResponse

class RequestService:
    def __init__(
        self,
        guild_repo: GuildRepository,
        member_service: MemberService,
        role_repo: RoleRepository,
        permission_repo: PermissionRepository,
        cache: RedisRepository
        ):
        self.guild_repo = guild_repo
        self.member_service = member_service
        self.role_repo = role_repo
        self.permission_repo = permission_repo
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
        
        print(not EnumPermissions.invite_members.value in member.role.permissions)
        
        if member.guild_tag != tag and member.user_id != guild.owner_id and \
        not EnumPermissions.invite_members.value in member.role.permissions:
            raise MemberNotHavePermissionException
    
    
    async def get_requests_by_guild_tag(self, tag: str, user_id: int) -> List[RequestResponse]:
        await self.validate_guild_member(tag, user_id)
        requests = await self.cache.get_requests(tag)
        return [cache_to_dto(r) for r in requests]
    
    
    async def add_request(self, tag: str, user_id: int) -> None:
        try:
            await self.member_service.get_user_by_id(user_id)
            raise MemberAlreadyInGuildException
        except MemberNotFoundException:
            pass
        
        if not validate_str(tag):
            raise UncorrectGuildTagException
        
        guild = await self.guild_repo.get_by_tag(tag)
        if not guild:
            raise GuildNotFoundException
        
        if guild.is_full:
            raise GuildIsFullException
        
        check = await self.cache.check_request(tag, user_id)
        if check:
            raise RequestAlreadyExistException
        
        await self.cache.add_request(tag, user_id)
    
    
    async def cancel_request(self, tag: str, guild_user_id: int, user_id: int) -> None:
        await self.validate_guild_member(tag, guild_user_id)
        
        check = await self.cache.check_request(tag, user_id)
        if not check:
            raise RequestNotFoundException
        
        try:
            await self.member_service.get_user_by_id(user_id)
            raise MemberAlreadyInGuildException
        except MemberNotFoundException:
            pass
        
        await self.cache.remove_request(tag, user_id)
    
    
    async def apply_request(self, tag: str, guild_user_id: int, user_id: int) -> MemberResponse:
        await self.validate_guild_member(tag, guild_user_id)
        
        check = await self.cache.check_request(tag, user_id)
        if not check:
            raise RequestNotFoundException
        
        try:
            await self.member_service.get_user_by_id(user_id)
            raise MemberAlreadyInGuildException
        except MemberNotFoundException:
            pass
        
        await self.cache.remove_request(tag, user_id)
        
        await self.member_service.add_member(tag, guild_user_id, AddMemberRequest(user_id=user_id, user_name=None))