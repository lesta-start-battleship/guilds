from typing import List, Optional

from repositories.guild import GuildRepository
from repositories.member import MemberRepository
from repositories.role import RoleRepository

from db.models.guild import Guild

from exceptions.guild import UncorrectGuildTagException, GuildNotFoundException, GuildAlreadyExistException
from exceptions.member import MemberIsNotOwnerException, MemberAlreadyInGuildException, MemberNotFoundException
from exceptions.role import RoleNotFoundException

from services.converters import guild_orm_to_dto
from utils.string_validator import validate_str

from schemas.guild import EditGuildRequest, GuildResponse, CreateGuildRequest

class GuildService:
    def __init__(self, guild_repo: GuildRepository, member_repo: MemberRepository, role_repo: RoleRepository):
        self.guild_repo = guild_repo
        self.member_repo = member_repo
        self.role_repo = role_repo
    
    
    async def get_guild_by_tag(self, tag: str) -> GuildResponse:
        if not validate_str(tag):
            raise UncorrectGuildTagException
        
        guild = await self.guild_repo.get_by_tag(tag)
        if not guild:
            raise GuildNotFoundException
        
        return guild_orm_to_dto(guild)
    
    
    async def get_guild_list(self, limit, offset) -> List[GuildResponse]:
        guilds = await self.guild_repo.get_guilds(limit, offset)
        return [guild_orm_to_dto(guild) for guild in guilds]
    
    
    async def create_guild(
        self,
        guild_req: CreateGuildRequest,
        user_id: int,
        user_name: Optional[str]
        ) -> GuildResponse:
        if not validate_str(guild_req.tag):
            raise UncorrectGuildTagException
        
        if await self.guild_repo.get_by_tag(guild_req.tag):
            raise GuildAlreadyExistException
    
        if await self.member_repo.get_by_user_id(user_id):
            return MemberAlreadyInGuildException
            
        new_guild = await self.guild_repo.create(
            owner_id=user_id,
            tag=guild_req.tag,
            title=guild_req.title,
            description=guild_req.desciption,
            )
        
        if not new_guild:
            raise GuildNotFoundException
            
        owner = await self.member_repo.add_member(new_guild.id, new_guild.tag, user_id, user_name)
        if not owner:
            raise MemberNotFoundException
        
        role = await self.role_repo.get_by_title('owner')
        if not role:
            return RoleNotFoundException
        
        if not await self.member_repo.edit(user_id=owner.user_id, role_id=role.id):
            raise MemberNotFoundException
        
        return guild_orm_to_dto(new_guild)
    
    
    async def edit_guild(self, tag: str, user_id: int, edit_form: EditGuildRequest) -> GuildResponse:
        if not validate_str(tag):
            raise UncorrectGuildTagException
        
        guild = await self.guild_repo.get_by_tag(tag)
        if not guild:
            raise GuildNotFoundException
        
        if guild.owner_id != user_id:
            raise MemberIsNotOwnerException
            
        guild = await self.guild_repo.edit(tag, edit_form.title, edit_form.desciption)
        return guild_orm_to_dto(guild)
    
    
    async def delete_guild(self, tag: str, user_id: int) -> None:
        guild = await self.guild_repo.get_by_tag(tag)
        
        if not guild:
            raise GuildNotFoundException
        
        if guild.owner_id != user_id:
            raise MemberIsNotOwnerException
        
        await self.guild_repo.delete(tag)