from datetime import datetime
from typing import Dict

from db.models.guild import Guild, Member, Role
from schemas.guild import GuildResponse
from schemas.member import MemberResponse
from schemas.role import RoleResponse
from schemas.guild_request import RequestResponse

def guild_orm_to_dto(guild: Guild) -> GuildResponse:
    return GuildResponse(
        tag=guild.tag,
        title=guild.title,
        description=guild.description,
        id=guild.id,
        owner_id=guild.owner_id,
        is_active=guild.is_active,
        is_full=guild.is_full
    )

def member_orm_to_dto(member: Member) -> MemberResponse:
    return MemberResponse(
        user_id=member.user_id,
        user_name=member.user_name,
        guild_id=member.guild_id,
        guild_tag=member.guild_tag,
        role=role_orm_to_dto(member.role)
    )
    
def role_orm_to_dto(role: Role) -> RoleResponse:
    return RoleResponse(
        id=role.id,
        title=role.title,
        permissions=set([p.permission for p in role.permissions])
    )

def cache_to_dto(cache: Dict[str, str]) -> RequestResponse:
    return RequestResponse(
        user_id=int(cache['user_id']),
        # user_name=cache['user_name'],
        created_at=cache['created_at']
    )