from domain.entities.guild import Guild, Member, Role
from domain.entities.guild_request import GuildJoinRequest
from schemas.guild import GuildResponse
from schemas.member import MemberResponse
from schemas.role import RoleResponse
from schemas.guild_request import RequestResponse


def guild_domain_to_dto(guild: Guild) -> GuildResponse:
    return GuildResponse(
        id=guild.id,
        tag=str(guild.tag),
        title=guild.title,
        description=guild.description,
        owner_id=guild.owner_id,
        is_active=guild.is_active,
        is_full=guild.is_full
    )

def member_domain_to_dto(member: Member) -> MemberResponse:
    return MemberResponse(
        user_id=member.user_id,
        user_name=member.username,
        guild_id=member.guild_id,
        guild_tag=str(member.guild_tag),
        role=role_domain_to_dto(member.role)
    )
    
def role_domain_to_dto(role: Role) -> RoleResponse:
    return RoleResponse(
        id=role.id,
        title=role.title,
        permissions=role.permissions,
        promote_roles=role.promote_roles
    )

def request_domain_to_dto(request: GuildJoinRequest) -> RequestResponse:
    return RequestResponse(
        user_id=request.user_id,
        user_name=request.username,
        guild_tag=str(request.guild_tag),
        created_at=request.created_at
    )