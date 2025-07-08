from datetime import datetime
from typing import Dict

from infra.db.models.guild import GuildORM, MemberORM, RoleORM
from domain.entities.guild import Guild, Member, Role
from domain.values.tag import Tag
from domain.entities.guild_request import GuildJoinRequest


def guild_orm_to_domain(guild: GuildORM) -> Guild:
    return Guild(
        id=guild.id,
        tag=Tag(guild.tag),
        title=guild.title,
        description=guild.description,
        owner_id=guild.owner_id,
        members={m.user_id: m.role_id for m in guild.members}
    )

def member_orm_to_domain(member: MemberORM) -> Member:
    return Member(
        id=member.id,
        user_id=member.user_id,
        username=member.user_name,
        guild_id=member.guild_id,
        guild_tag=Tag(member.guild_tag),
        role=role_orm_to_domain(member.role)
    )

def role_orm_to_domain(role: RoleORM) -> Role:
    return Role(
        id=role.id,
        title=role.title,
        permissions=set([p.permission for p in role.permissions]),
        promote_roles=set([r.id for r in role.promote_roles])
    )

def cache_to_domain(request: Dict[str, object]) -> GuildJoinRequest:
    return GuildJoinRequest(
        guild_tag=Tag(request['tag']),
        user_id=request['user_id'],
        username=request['user_name'],
        created_at=datetime.fromisoformat(request['created_at']),
        status='pending'
    )