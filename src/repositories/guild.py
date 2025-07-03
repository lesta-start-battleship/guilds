from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.models.guild import Guild

class GuildRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        
        
    async def get_by_id(self, guild_id: int) -> Optional[Guild]:
        result = await self.session.execute(
            select(Guild).
            options(selectinload(Guild.members)).
            where(Guild.id == guild_id)
            )
        
        return result.scalar_one_or_none()
    
    
    async def get_by_tag(self, tag: str) -> Optional[Guild]:
        result = await self.session.execute(
            select(Guild).
            where(Guild.tag == tag)
            )
        
        return result.scalar_one_or_none()
    
    
    async def get_by_owner_id(self, owner_id: int) -> Optional[Guild]:
        result = await self.session.execute(
            select(Guild).
            where(Guild.owner_id == owner_id)
            )
        
        return result.scalar_one_or_none()

    async def get_guilds(self, limit: int = 10, offset: int = 0) -> Optional[List[Guild]]:
        result = await self.session.execute(
            select(Guild).
            limit(limit).
            offset(offset)
        )
        return result.scalars().all()

    async def create(
        self,
        owner_id: int,
        tag: str,
        title: Optional[str],
        description: Optional[str]
        ) -> Optional[Guild]:
        
        guild = Guild(owner_id=owner_id, tag=tag, title=title, description=description)
        self.session.add(guild)
        await self.session.commit()
        
        return guild
    
    
    async def delete(self, guild_id) -> bool:
        guild = await self.get_by_id(guild_id)
        
        if guild:
            await self.session.delete(guild)
            await self.session.commit()
            return True
        return False
        
        
    async def edit(
        self,
        guild_id: int,
        title: Optional[str],
        description: Optional[str]
        ) -> Optional[Guild]:
        
        guild = await self.get_by_id(guild_id)
        
        if guild:
            if title:
                guild.title = title
            if description:
                guild.description = description
                
            await self.session.flush(guild)
            await self.session.commit()
            
        return guild