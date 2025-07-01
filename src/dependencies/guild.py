from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.repositories.guild import GuildRepository
from src.repositories.member import MemberRepository
from src.repositories.role import RoleRepository

def get_guild_repository(session: AsyncSession = Depends(get_db)):
    return GuildRepository(session)

def get_member_repository(session: AsyncSession = Depends(get_db)):
    return MemberRepository(session)

def get_role_repository(session: AsyncSession = Depends(get_db)):
    return RoleRepository(session)