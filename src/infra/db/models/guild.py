from typing import List

from sqlalchemy import Column, Integer, String, ForeignKey, Table, Text, DateTime, func, Boolean, Enum as SqlEnum
from sqlalchemy.orm import relationship, mapped_column, Mapped

from infra.db.database import Base

from domain.values.permission import Permission


class GuildORM(Base):
    __tablename__ = "guilds"

    id = Column(Integer, primary_key=True, index=True)
    tag = Column(String, unique=True, index=True)
    description = Column(String, unique=False, index=False)
    title = Column(String, unique=False, index=False)
    owner_id = Column(Integer)
    
    is_active = Column(Boolean, default=False)
    is_full = Column(Boolean, default=False)

    members = relationship("MemberORM", back_populates="guild", cascade="all, delete-orphan")


roles_promotes_table = Table(
    'roles_promotes',
    Base.metadata,
    Column('role_id', ForeignKey('roles.id'), primary_key=True),
    Column('promote_role_id', ForeignKey('roles.id'), primary_key=True)
)


class RoleORM(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=False)
    title = Column(String, index=False)

    members = relationship("MemberORM", back_populates="role")
    
    permissions: Mapped[List['PermissionORM']] = relationship(
        'PermissionORM',
        secondary='role_permission',
        back_populates='roles'
    )
    
    promote_roles = relationship(
        'RoleORM',
        secondary=roles_promotes_table,
        primaryjoin=id == roles_promotes_table.c.role_id,
        secondaryjoin=id == roles_promotes_table.c.promote_role_id,
        back_populates='promoted_by_roles'
    )
    
    promoted_by_roles = relationship(
        'RoleORM',
        secondary=roles_promotes_table,
        primaryjoin=id == roles_promotes_table.c.promote_role_id,
        secondaryjoin=id == roles_promotes_table.c.role_id,
        back_populates='promote_roles'
    )


class PermissionORM(Base):
    __tablename__ = 'permissions'
    
    id = Column(Integer, primary_key=True, index=False)
    permission = Column(SqlEnum(Permission, name='permission'), unique=True, nullable=False)

    roles: Mapped[List['RoleORM']] = relationship(
        'RoleORM',
        secondary='role_permission',
        back_populates='permissions'
    )
    

class RolePermissionORM(Base):
    __tablename__ = 'role_permission'
    
    role_id: Mapped[int] = mapped_column(ForeignKey('roles.id'), primary_key=True)
    permission_id: Mapped[int] = mapped_column(ForeignKey('permissions.id'), primary_key=True)


class MemberORM(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)

    guild_id = Column(Integer, ForeignKey("guilds.id"))
    guild_tag = Column(String)
    role_id = Column(Integer, ForeignKey("roles.id"))

    user_name = Column(String, index=True, nullable=True)

    guild = relationship("GuildORM", back_populates="members")
    role = relationship("RoleORM", back_populates="members")


class GuildChatMessage(Base):
    __tablename__ = "guild_chat_messages"

    id = Column(Integer, primary_key=True, index=True)  # проставили индексы для более быстрой работы БД
    guild_id = Column(Integer, ForeignKey("guilds.id"), index=True)
    user_id = Column(Integer, index=True)

    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    guild = relationship("GuildORM", backref="chat_messages")
