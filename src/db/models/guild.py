from typing import List
from enum import Enum

from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, func, Boolean, Enum as SqlEnum
from sqlalchemy.orm import relationship, mapped_column, Mapped

from db.database import Base


class Guild(Base):
    __tablename__ = "guilds"

    id = Column(Integer, primary_key=True, index=True)
    tag = Column(String, unique=True, index=True)
    description = Column(String, unique=False, index=False)
    title = Column(String, unique=False, index=False)
    owner_id = Column(Integer)
    
    is_active = Column(Boolean, default=False)
    is_full = Column(Boolean, default=False)

    members = relationship("Member", back_populates="guild", cascade="all, delete-orphan")


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=False)
    title = Column(String, index=False)

    members = relationship("Member", back_populates="role")
    
    permissions: Mapped[List['Permission']] = relationship(
        'Permission',
        secondary='role_permission',
        back_populates='roles'
    )


class EnumPermissions(Enum):
    owner = 'owner'
    invite_members = 'invite_members'
    kick_members = 'kick_members'
    promote_members = 'promote_members'
    wars = 'wars'


class Permission(Base):
    __tablename__ = 'permissions'
    
    id = Column(Integer, primary_key=True, index=False)
    permission = Column(SqlEnum(EnumPermissions, name='permission'), nullable=False)

    roles: Mapped[List['Role']] = relationship(
        'Role',
        secondary='role_permission',
        back_populates='permissions'
    )
    

class RolePermission(Base):
    __tablename__ = 'role_permission'
    
    role_id: Mapped[int] = mapped_column(ForeignKey('roles.id'), primary_key=True)
    permission_id: Mapped[int] = mapped_column(ForeignKey('permissions.id'), primary_key=True)


class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)

    guild_id = Column(Integer, ForeignKey("guilds.id"))
    guild_tag = Column(String)
    role_id = Column(Integer, ForeignKey("roles.id"), default=0)

    user_name = Column(String, unique=True, index=True, nullable=True)

    guild = relationship("Guild", back_populates="members")
    role = relationship("Role", back_populates="members")


class GuildChatMessage(Base):
    __tablename__ = "guild_chat_messages"

    id = Column(Integer, primary_key=True, index=True)  # проставили индексы для более быстрой работы БД
    guild_id = Column(Integer, ForeignKey("guilds.id"), index=True)
    user_id = Column(Integer, index=True)

    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    guild = relationship("Guild", backref="chat_messages")
