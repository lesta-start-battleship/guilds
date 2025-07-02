from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.domain.models.guild import Guild, Tag
from src.domain.repositories.guild_repo import GuildRepository
from src.infra.db.models.guild import GuildDB

class SQLGuildRepository(GuildRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        
        
    async def get_by_id(self, guild_id: int) -> Optional[Guild]:
        result = await self.session.execute(
            select(Guild).
            options(selectinload(Guild.members)).
            where(Guild.id == guild_id)
            )
        guild  = result.scalar_one_or_none()
        
        if not guild:
            return None
        
        return Guild(
            id=guild.id,
            tag=Tag(guild.tag),
            title=guild.title,
            description=guild.description,
            owner_id=guild.owner_id)
    
    
    async def get_by_tag(self, tag: str) -> Optional[Guild]:
        result = await self.session.execute(
            select(Guild).
            where(Guild.tag == tag)
            )
        guild  = result.scalar_one_or_none()
        
        if not guild:
            return None
        
        return Guild(
            id=guild.id,
            tag=Tag(guild.tag),
            title=guild.title,
            description=guild.description,
            owner_id=guild.owner_id)
        
    
    async def list_guilds(self, offset: int = 0, limit: int = 10) -> Optional[List[Guild]]:
        result = self.session.execute(
            select(Guild).
            limit(limit=limit).
            offset(offset=offset)
            )
        
        guilds = result.scalars().all()
        
        return [
            Guild(
                id=guild.id,
                tag=Tag(guild.tag),
                title=guild.title,
                description=guild.description,
                owner_id=guild.owner_id)
            for guild in guilds
            ]
        
        
    async def create(self, guild: Guild) -> Optional[Guild]:
        guild = GuildDB(
            owner_id=guild.owner_id,
            tag=guild.tag, 
            title=guild.title,
            description=guild.description
            )
        self.session.add(guild)
        await self.session.commit()
        
        return guild
    
    
    async def delete(self, guild_id) -> None:
        guild = await self.get_by_id(guild_id)
        
        if guild:
            await self.session.delete(guild)
            await self.session.commit()
        
        
    async def edit(self, guild_id: int, title: Optional[str], description: Optional[str]) -> Optional[Guild]:
        
        guild = await self.get_by_id(guild_id)
        
        if not guild:
            return None
        
        if title:
            guild.title = title
        if description:
            guild.description = description
            
        await self.session.flush(guild)
        await self.session.commit()
        
        return Guild(
            id=guild.id,
            tag=Tag(guild.tag),
            title=guild.title,
            description=guild.description,
            owner_id=guild.owner_id)