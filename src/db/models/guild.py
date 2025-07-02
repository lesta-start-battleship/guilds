from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, func, Boolean

from sqlalchemy.orm import relationship
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
    
    edit = Column(Boolean)
    owner = Column(Boolean)
    
    title = Column(String, index=False)

    members = relationship("Member", back_populates="role")


class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)

    guild_id = Column(Integer, ForeignKey("guilds.id"))
    role_id = Column(Integer, ForeignKey("roles.id"), default=0)

    user_name = Column(String, index=True)

    guild = relationship("Guild", back_populates="members")
    role = relationship("Role", back_populates="members")


class GuildChatMessage(Base):
    __tablename__ = "guild_chat_messages"

    id = Column(Integer, primary_key=True, index=True) # проставили индексы для более быстрой работы БД
    guild_id = Column(Integer, ForeignKey("guilds.id"), index=True)
    user_id = Column(Integer, index=True)

    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    guild = relationship("Guild", backref="chat_messages")
