from typing import List, Tuple

from domain.exceptions.member import MemberNotFoundException
from domain.repositories.member_repo import MemberRepositoryBase

from domain.values.tag import Tag
from services.converters.domain_to_dto import member_domain_to_dto

from schemas.member import MemberResponse

class MemberService:
    def __init__(self, member_repo: MemberRepositoryBase):
        self.member_repo = member_repo
    
    async def get_user_by_id(self, user_id: int) -> MemberResponse:
        member = await self.member_repo.get_by_id(user_id)
        if not member:
            raise MemberNotFoundException(user_id)
        return member_domain_to_dto(member)
    
    
    async def get_guild_members(self, tag: str, limit: int, offset: int) -> Tuple[List[MemberResponse], int]:
        valid_tag = Tag(tag)
        members, count = await self.member_repo.list_members_by_guild_tag(str(valid_tag), offset, limit)
        return [member_domain_to_dto(member) for member in members], count
    
    
    async def get_members_by_guild_id(self, guild_id: int) -> List[int]:
        members = await self.member_repo.list_members_by_guild_id(guild_id)
        return [member.user_id for member in members]
    
    
    async def on_username_changed(self, user_id: int, username: str):
        member = await self.member_repo.get_by_id(user_id)
        if member:
            member.username = username
            await self.member_repo.save(member)