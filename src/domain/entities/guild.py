from dataclasses import dataclass, field
from typing import Dict, Optional, Set

from domain.exceptions.guild import GuildIsFullException
from domain.exceptions.member import MemberAlreadyInGuildException, MemberNotFoundException, MemberNotHavePermissionException, MemberNotOwnerException
from domain.values.permission import Permission
from domain.values.tag import Tag
from settings import settings


@dataclass
class Role:
    id: int
    title: str
    permissions: Set[Permission]
    promote_roles: Set[int]


@dataclass
class Member:
    user_id: int
    username: str
    guild_id: int
    guild_tag: Tag
    role: Optional[Role] = None
    id: Optional[int] = None


@dataclass
class Guild:
    
    tag: Tag
    owner_id: int
    members: Dict[int, int] = field(default_factory=dict)
    title: Optional[str] = None
    description: Optional[str] = None
    id: Optional[int] = None

    @property
    def is_active(self) -> bool:
        return self.members_count >= settings.min_members

    @property
    def is_full(self) -> bool:
        return self.members_count >= settings.max_members
    
    @property
    def members_count(self) -> int:
        return len(self.members)
    
    
    def edit_title_description(self, member_id: int, title: Optional[str] = None, description: Optional[str] = None):
        if member_id != self.owner_id:
            raise MemberNotOwnerException(member_id)
        
        if title:
            self.title = title
        if description:
            self.description = description
    
    
    def add_member(self, user_id: int, role_id: int, member_id: int, member_role: Role):
        if self.is_full:
            raise GuildIsFullException(self.tag)
        
        if user_id in self.members:
            raise MemberAlreadyInGuildException()
        
        if member_id not in self.members:
            raise MemberNotFoundException(member_id)
        
        if not (Permission.invite_members in member_role.permissions \
        and role_id in member_role.promote_roles):
            raise MemberNotHavePermissionException(member_id)
        
        self.members[user_id] = role_id
    
    
    def remove_member(self, target_member_id: int, member_id: int, member_role: Role, target_member_role: Role):
        if target_member_id == member_id or target_member_id == self.owner_id:
            raise MemberNotHavePermissionException(member_id)
        
        if target_member_id not in self.members:
            raise MemberNotFoundException(target_member_id)
        
        if member_id not in self.members:
            raise MemberNotFoundException(member_id)
        
        if not (Permission.kick_members in member_role.permissions \
        and target_member_role.id in member_role.promote_roles):
            raise MemberNotHavePermissionException(member_id)
        
        del self.members[target_member_id]
    
    
    def promote_member(
        self,
        target_member_id: int,
        member_id: int,
        member_role: Role,
        old_role: Role,
        new_role: Role
        ):
        if target_member_id == member_id:
            raise MemberNotHavePermissionException(member_id)
        
        if target_member_id not in self.members:
            raise MemberNotFoundException(target_member_id)
        
        if member_id not in self.members:
            raise MemberNotFoundException(member_id)
        
        if not(Permission.promote_members in member_role.permissions \
        and old_role.id in member_role.promote_roles \
        and new_role.id in member_role.promote_roles):
            raise MemberNotHavePermissionException(member_id)
        
        self.members[target_member_id] = new_role.id
    
    
    def leave_guild(self, member_id: int):
        if self.owner_id == member_id:
            raise MemberNotHavePermissionException(member_id)
        
        if member_id not in self.members:
            raise MemberNotFoundException(member_id)
        
        del self.members[member_id]