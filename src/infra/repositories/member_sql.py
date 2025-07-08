from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from infra.db.models.guild import MemberORM, RoleORM

from domain.entities.guild import Member
from domain.repositories.member_repo import MemberRepositoryBase

from services.converters.orm_to_domain import member_orm_to_domain


class SQLMemberRepository(MemberRepositoryBase):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, user_id: int):
        result = await self.session.execute(
            select(MemberORM).
            options(
                selectinload(MemberORM.role),
                selectinload(MemberORM.role).selectinload(RoleORM.permissions),
                selectinload(MemberORM.role).selectinload(RoleORM.promote_roles)
            ).
            where(MemberORM.user_id == user_id)
        )

        member = result.scalar_one_or_none()
        return member_orm_to_domain(member) if member else None
    
    
    async def list_members_by_guild_tag(self, guild_tag: str, offset: int = 0, limit: int = 10):
        result = await self.session.execute(
            select(MemberORM).
            options(
                selectinload(MemberORM.role),
                selectinload(MemberORM.role).selectinload(RoleORM.permissions),
                selectinload(MemberORM.role).selectinload(RoleORM.promote_roles)
            ).
            where(MemberORM.guild_tag == guild_tag).
            limit(limit).
            offset(offset)
        )
        
        members = result.scalars().all()
        return [member_orm_to_domain(member) for member in members]
    
    
    async def list_members_by_guild_id(self, guild_id: int):
        result = await self.session.execute(
            select(MemberORM).
            options(
                selectinload(MemberORM.role),
                selectinload(MemberORM.role).selectinload(RoleORM.permissions),
                selectinload(MemberORM.role).selectinload(RoleORM.promote_roles)
            ).
            where(MemberORM.guild_id == guild_id)
        )

        members = result.scalars().all()
        return [member_orm_to_domain(member) for member in members]
    
    
    async def save(self, member: Member):
        existing = await self.session.get(MemberORM, member.id) if member.id else None

        if existing:
            existing.user_id = member.user_id
            existing.user_name = member.username
            existing.guild_id = member.guild_id
            existing.guild_tag = str(member.guild_tag)
            existing.role_id = member.role.id if member.role else None
        else:
            member_orm = MemberORM(
                user_id=member.user_id,
                user_name=member.username,
                guild_id=member.guild_id,
                guild_tag=str(member.guild_tag),
                role_id=member.role.id if member.role else None
            )
            self.session.add(member_orm)
            
        await self.session.commit()
    
    async def create(self, member: Member):
        member_orm = MemberORM(
            user_id=member.user_id,
            user_name=member.username,
            guild_id=member.guild_id,
            guild_tag=str(member.guild_tag),
            role_id=member.role.id if member.role else None
        )
        
        self.session.add(member_orm)
        await self.session.commit()
        
        return await self.get_by_id(member.user_id)
    
    
    async def delete(self, user_id: int):
        member_orm = await self.session.scalar(select(MemberORM).where(MemberORM.user_id == user_id))
        if member_orm:
            await self.session.delete(member_orm)
            await self.session.commit()
    
    
    async def exists_by_id(self, user_id: int):
        result = await self.session.execute(
            select(MemberORM.user_id).where(MemberORM.user_id == user_id)
        )
        return result.scalar_one_or_none() is not None