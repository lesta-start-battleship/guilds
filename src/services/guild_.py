from typing import List, Tuple

from domain.entities.guild import Guild, Member

from domain.exceptions.guild import GuildAlreadyExistsException, GuildNotExistsException
from domain.exceptions.member import MemberAlreadyInGuildException, MemberNotFoundException, MemberNotOwnerException
from domain.exceptions.role import RoleNotFoundException
from domain.repositories.guild_repo import GuildRepositoryBase
from domain.repositories.member_repo import MemberRepositoryBase
from domain.repositories.producer import ProducerBase
from domain.repositories.role_repo import RoleRepositoryBase

from domain.values.tag import Tag
from schemas.guild import CreateGuildRequest, EditGuildRequest, GuildResponse

from schemas.member import MemberResponse
from services.converters.domain_to_dto import guild_domain_to_dto, member_domain_to_dto

class GuildService:
    def __init__(
        self,
        guild_repo: GuildRepositoryBase,
        member_repo: MemberRepositoryBase,
        role_repo: RoleRepositoryBase,
        producer: ProducerBase
        ):
        self.guild_repo = guild_repo
        self.member_repo = member_repo
        self.role_repo = role_repo
        self.producer = producer
    
    async def get_by_tag(self, tag: str) -> GuildResponse:
        valid_tag = Tag(tag)
        guild = await self.guild_repo.get_by_tag(str(valid_tag))
        if not guild:
            raise GuildNotExistsException(valid_tag)
        return guild_domain_to_dto(guild)
    
    
    async def get_by_owner_id(self, user_id: int) -> GuildResponse:
        guild = await self.guild_repo.get_by_owner_id(user_id)
        if not guild:
            raise MemberNotOwnerException(user_id)
        return guild_domain_to_dto(guild)
    
    
    async def get_guild_list(self, limit: int, offset: int) -> Tuple[List[GuildResponse], int]:
        guilds, count = await self.guild_repo.list_guilds(offset, limit)
        return [guild_domain_to_dto(guild) for guild in guilds], count
    
    
    async def create_guild(
        self,
        guild_req: CreateGuildRequest,
        user_id: int,
        user_name: str
        ) -> GuildResponse:
        tag = Tag(guild_req.tag)
        
        if await self.guild_repo.exists_by_tag(str(tag)):
            raise GuildAlreadyExistsException(tag)
        
        if await self.member_repo.exists_by_id(user_id):
            raise MemberAlreadyInGuildException(user_id)
        
        guild = Guild(
            tag=tag,
            title=guild_req.title,
            description=guild_req.description,
            owner_id=user_id
        )
        guild = await self.guild_repo.create(guild)
        
        role = await self.role_repo.get_by_title('owner')
        if not role:
            raise RoleNotFoundException('owner')
        
        member = Member(
            user_id=user_id,
            username=user_name,
            guild_id=guild.id,
            guild_tag=tag,
            role=role
        )
        await self.member_repo.create(member)
        self.producer.publish_guild_created(guild.id, str(guild.tag), guild.owner_id)
        return guild_domain_to_dto(guild)
    
    
    async def edit_guild(self, tag: str, user_id: int, edit_form: EditGuildRequest) -> GuildResponse:
        guild = await self.guild_repo.get_by_tag(str(Tag(tag)))
        guild.edit_title_description(user_id, title=edit_form.title, description=edit_form.description)
        await self.guild_repo.save(guild)
        
        return guild_domain_to_dto(guild)
    
    
    async def delete_guild(self, tag: str, user_id: int) -> str:
        valid_tag = Tag(tag)
        if not await self.guild_repo.exists_by_tag(str(valid_tag)):
            raise GuildNotExistsException(tag)
        
        guild = await self.guild_repo.get_by_tag(str(valid_tag))
        if guild.owner_id != user_id:
            raise MemberNotOwnerException(user_id)
        
        await self.guild_repo.delete(str(valid_tag))
        self.producer.publish_guild_deleted(guild.id)
        return str(valid_tag)
        
    
    async def add_member(self, tag: str, member_id: int, user_id: int, username: str) -> MemberResponse:
        valid_tag = Tag(tag)
        guild = await self.guild_repo.get_by_tag(str(valid_tag))
        if not guild:
            raise GuildNotExistsException(valid_tag)
        
        guild_member = await self.member_repo.get_by_id(member_id)
        if not guild_member:
            raise MemberNotFoundException(member_id)
        
        if await self.member_repo.exists_by_id(user_id):
            raise MemberAlreadyInGuildException(user_id)
        
        role = await self.role_repo.get_by_title('cabin_boy')
        if not role:
            raise RoleNotFoundException('cabin_boy')
        
        member = Member(
            user_id=user_id,
            username=username,
            guild_id=guild.id,
            guild_tag=tag,
            role=role
        )
        
        guild.add_member(user_id, role.id, guild_member.user_id, guild_member.role)
        member = await self.member_repo.create(member)
        self.producer.publish_guild_member_count_changed(guild.id, user_id, guild.members_count)
        return member_domain_to_dto(member)
    
    
    async def change_member_role(self, tag: str, member_id: int, target_user_id: int, role_id: int) -> MemberResponse:
        valid_tag = Tag(tag)
        guild = await self.guild_repo.get_by_tag(str(valid_tag))
        if not guild:
            raise GuildNotExistsException(valid_tag)
        
        guild_member = await self.member_repo.get_by_id(member_id)
        if not guild_member:
            raise MemberNotFoundException(member_id)
        
        member = await self.member_repo.get_by_id(target_user_id)
        if not member:
            raise MemberNotFoundException(target_user_id)
        
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise RoleNotFoundException(role_id)
        
        guild.promote_member(member.user_id, guild_member.user_id, guild_member.role, member.role, role)
        member.role = role
        await self.member_repo.save(member)
        return member_domain_to_dto(member)
    
    
    async def remove_member(self, tag: str, target_user_id: int, member_id: int) -> None:
        valid_tag = Tag(tag)
        guild = await self.guild_repo.get_by_tag(str(valid_tag))
        if not guild:
            raise GuildNotExistsException(valid_tag)
        
        guild_member = await self.member_repo.get_by_id(member_id)
        if not guild_member:
            raise MemberNotFoundException(member_id)
        
        member = await self.member_repo.get_by_id(target_user_id)
        if not member:
            raise MemberNotFoundException(target_user_id)
        
        guild.remove_member(member.user_id, guild_member.user_id, guild_member.role, member.role)
        await self.member_repo.delete(member.user_id)
        self.producer.publish_guild_member_count_changed(guild.id, target_user_id, guild.members_count)
        
    
    async def leave_guild(self, tag: str, member_id: int) -> None:
        valid_tag = Tag(tag)
        guild = await self.guild_repo.get_by_tag(str(valid_tag))
        if not guild:
            raise GuildNotExistsException(valid_tag)
        
        guild_member = await self.member_repo.get_by_id(member_id)
        if not guild_member:
            raise MemberNotFoundException(member_id)
        
        guild.leave_guild(guild_member.user_id)
        await self.member_repo.delete(guild_member.user_id)
        self.producer.publish_guild_member_count_changed(guild.id, member_id, guild.members_count)