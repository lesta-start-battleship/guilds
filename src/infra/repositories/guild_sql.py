from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from infra.db.models.guild import GuildORM, MemberORM

from domain.entities.guild import Guild
from domain.repositories.guild_repo import GuildRepositoryBase

from services.converters.orm_to_domain import guild_orm_to_domain


class SQLGuildRepository(GuildRepositoryBase):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, guild_id: int):
        result = await self.session.execute(
            select(GuildORM).
            options(selectinload(GuildORM.members)).
            where(GuildORM.id == guild_id)
        )
        
        guild = result.scalar_one_or_none()
        return guild_orm_to_domain(guild) if guild else None
    
    
    async def get_by_tag(self, tag: str):
        result = await self.session.execute(
            select(GuildORM).
            options(selectinload(GuildORM.members)).
            where(GuildORM.tag == tag)
        )
        
        guild = result.scalar_one_or_none()
        return guild_orm_to_domain(guild) if guild else None
    
    
    async def get_by_owner_id(self, owner_id: int):
        result = await self.session.execute(
            select(GuildORM).
            options(selectinload(GuildORM.members)).
            where(GuildORM.owner_id == owner_id)
        )
        
        guild = result.scalar_one_or_none()
        return guild_orm_to_domain(guild) if guild else None
    
    
    async def list_guilds(self, page: int = 1, limit: int = 10):
        result = await self.session.execute(
            select(GuildORM).
            options(selectinload(GuildORM.members).selectinload(MemberORM.role)).
            limit(limit).
            offset((page-1)*limit)
        )
        guilds = result.scalars().all()
        
        count_stmt = select(func.count()).select_from(select(GuildORM).subquery())
        total = (await self.session.execute(count_stmt)).scalar_one()
        return [guild_orm_to_domain(guild) for guild in guilds], total
    
    
    async def save(self, guild: Guild):
        existing = await self.session.get(GuildORM, guild.id) if guild.id else None

        if existing:
            existing.id = guild.id
            existing.tag = str(guild.tag)
            existing.owner_id = guild.owner_id
            existing.title = guild.title
            existing.description = guild.description
        else:
            guild_orm = GuildORM(
                id=guild.id,
                tag=str(guild.tag),
                title=guild.title,
                description=guild.description,
                owner_id=guild.owner_id
            )
            self.session.add(guild_orm)
            
        await self.session.commit()
    
    
    async def create(self, guild: Guild):
        guild_orm = GuildORM(
            tag=str(guild.tag),
            title=guild.title,
            description=guild.description,
            owner_id=guild.owner_id
        )
        
        self.session.add(guild_orm)
        await self.session.commit()
        
        return self.get_by_tag(str(guild.tag))
    
    
    async def delete(self, guild_tag: str) -> None:
        guild_orm = await self.session.scalar(select(GuildORM).where(GuildORM.tag == guild_tag))
        if guild_orm:
            await self.session.delete(guild_orm)
            await self.session.commit()
    
    
    async def exists_by_tag(self, tag: str) -> bool:
        result = await self.session.execute(
            select(GuildORM.tag).where(GuildORM.tag == tag)
        )
        return result.scalar_one_or_none() is not None