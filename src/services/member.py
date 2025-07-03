from repositories.guild import GuildRepository
from repositories.member import MemberRepository
from repositories.role import RoleRepository
from repositories.permisson import PermissionRepository

from db.models.guild import EnumPermissions

from exceptions.guild import GuildIsFullException, UncorrectGuildTagException, GuildNotFoundException
from exceptions.member import MemberInOtherGuildException, MemberAlreadyInGuildException, MemberNotFoundException, MemberNotHavePermissionException
from exceptions.role import RoleNotFoundException

from services.converters import member_orm_to_dto
from utils.string_validator import validate_str

from schemas.member import AddMemberRequest, MemberPagination, MemberResponse

from settings import settings

class MemberService:
    def __init__(
        self,
        guild_repo: GuildRepository,
        member_repo: MemberRepository,
        role_repo: RoleRepository,
        permission_repo: PermissionRepository):
        self.guild_repo = guild_repo
        self.member_repo = member_repo
        self.role_repo = role_repo
        self.permission_repo = permission_repo
    
    
    async def get_user_by_id(self, user_id: int) -> MemberResponse:
        member = await self.member_repo.get_by_user_id(user_id)
        if not member:
            raise MemberNotFoundException
        
        return member_orm_to_dto(member)
    
    
    async def get_guild_members(self, tag: str, limit: int, offset: int) -> MemberPagination:
        if not validate_str(tag):
            raise UncorrectGuildTagException
        
        if not await self.guild_repo.get_by_tag(tag):
            raise GuildNotFoundException
        
        members = await self.member_repo.get_list_by_guild_tag(tag, limit, offset)
        return [member_orm_to_dto(member) for member in members]
    
    
    async def delete_member(self, tag: str, guild_user_id: int, user_id: int) -> None:
        if not validate_str(tag):
            raise UncorrectGuildTagException
        
        guild = await self.guild_repo.get_by_tag(tag)
        if not guild:
            raise GuildNotFoundException
        
        guild_member = await self.member_repo.get_by_user_id(guild_user_id)
        if not guild_member:
            raise MemberNotFoundException
        
        if guild_member.guild_tag != tag or guild_user_id != guild.owner_id or \
        not self.permission_repo.get_by_title(EnumPermissions.kick_members) in guild_member.role.permissions:
            raise MemberNotHavePermissionException
            
        member = await self.member_repo.get_by_user_id(user_id)
        if not member:
            raise MemberNotFoundException
        
        if member.guild_tag != tag:
            raise MemberInOtherGuildException
        
        if member.id == guild.owner_id:
            raise MemberNotHavePermissionException
        
        members_count = await self.member_repo.get_members_count(member.guild_tag)
        if members_count == settings.max_members:
            self.guild_repo.edit(tag, is_full=False)
        elif members_count == settings.min_members:
            self.guild_repo.edit(tag, is_active=False)
        
        await self.member_repo.delete_member(user_id)
    
    
    async def exit_from_guild(self, tag: str, user_id: int) -> None:
        if not validate_str(tag):
            raise UncorrectGuildTagException
        
        guild = await self.guild_repo.get_by_tag(tag)
        if not guild:
            raise GuildNotFoundException
            
        member = await self.member_repo.get_by_user_id(user_id)
        if not member:
            raise MemberNotFoundException
        
        if member.guild_tag != tag:
            raise MemberInOtherGuildException
        
        if member.id == guild.owner_id:
            raise MemberNotHavePermissionException
        
        members_count = await self.member_repo.get_members_count(member.guild_tag)
        if members_count == settings.max_members:
            self.guild_repo.edit(tag, is_full=False)
        elif members_count == settings.min_members:
            self.guild_repo.edit(tag, is_active=False)
        
        await self.member_repo.delete_member(user_id)
    
    
    async def add_member(self, tag: str, guild_user_id: int, user_form: AddMemberRequest) -> MemberResponse:
        if not validate_str(tag):
            raise UncorrectGuildTagException
        
        guild = await self.guild_repo.get_by_tag(tag)
        if not guild:
            raise GuildNotFoundException
        
        guild_member = await self.member_repo.get_by_user_id(guild_user_id)
        if not guild_member:
            raise MemberNotFoundException
        
        if guild_member.guild_tag != tag or guild_user_id != guild.owner_id or \
        not self.permission_repo.get_by_title(EnumPermissions.invite_members) in guild_member.role.permissions:
            raise MemberNotHavePermissionException
        
        if await self.member_repo.get_by_user_id(user_form.user_id):
            raise MemberAlreadyInGuildException
        
        if await self.member_repo.get_members_count(tag) == settings.max_members:
            raise GuildIsFullException
        
        new_member = await self.member_repo.add_member(guild.id, guild.tag, user_form.user_id, user_form.user_name)
        
        members_count = await self.member_repo.get_members_count(tag)
        if members_count == settings.max_members:
            self.guild_repo.edit(tag, is_full=True)
        elif members_count == settings.min_members:
            self.guild_repo.edit(tag, is_active=True)
        
        return member_orm_to_dto(new_member)
    
    
    async def edit_member(
        self,
        tag: str,
        guild_user_id: int,
        user_id: int,
        role_id: int
        ) -> MemberResponse:
        if not validate_str(tag):
            raise UncorrectGuildTagException
        
        guild = await self.guild_repo.get_by_tag(tag)
        if not guild:
            raise GuildNotFoundException
        
        member = await self.member_repo.get_by_user_id(user_id)
        if not member:
            raise MemberNotFoundException
        
        if member.guild_tag != tag:
            raise MemberInOtherGuildException
        
        guild_member = await self.member_repo.get_by_user_id(guild_user_id)
        if not guild_member:
            raise MemberNotFoundException
        
        if guild_member.guild_tag != tag or guild_user_id != guild.owner_id or \
        not self.permission_repo.get_by_title(EnumPermissions.promote_members) in guild_member.role.permissions:
            raise MemberNotHavePermissionException
        
        if self.role_repo.get_by_id(role_id):
            raise RoleNotFoundException
        
        new_member = await self.member_repo.edit(user_id, role_id=role_id)
        return member_orm_to_dto(new_member)