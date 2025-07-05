from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from db.models.guild import Member, Role

class MemberRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_id(self, user_id: int) -> Optional[Member]:
        result = await self.session.execute(
            select(Member).
            options(
                selectinload(Member.role).selectinload(Role.permissions)
            ).
            where(Member.user_id == user_id)
        )

        return result.scalar_one_or_none()
    
    
    async def get_list_by_guild_tag(self, guild_tag: str, limit: int = 10, offset: int = 0) -> List[Member]:
        result = await self.session.execute(
            select(Member).
            options(
                selectinload(Member.role).selectinload(Role.permissions)
            ).
            where(Member.guild_tag == guild_tag).
            limit(limit=limit).
            offset(offset=offset)
        )

        return result.scalars().all()
    
    
    async def get_members_count(self, guild_tag: str) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(Member).where(Member.guild_tag == guild_tag)
        )
        
        return result.scalar_one()
    
    
    async def add_member(
        self,
        guild_id: int,
        guild_tag: str,
        new_user_id: int,
        user_name: Optional[str],
        role_id: Optional[int] = None
        ) -> Optional[Member]:
        
        member = Member(user_id=new_user_id, guild_id=guild_id, guild_tag=guild_tag, user_name=user_name, role_id=role_id)
        self.session.add(member)
        await self.session.commit()
        return member

    async def delete_member(self, user_id: int) -> bool:
        member = await self.get_by_user_id(user_id)
        if member:
            print('pipao')
            await self.session.delete(member)
            await self.session.commit()
            return True
        return False
    
    
    async def edit(
            self,
            user_id: Optional[int],
            role_id: Optional[int],
            user_name: Optional[str] = None,
    ) -> Optional[Member]:

        member = await self.get_by_user_id(user_id=user_id)

        if member:
            if user_name:
                member.user_name = user_name
            if role_id:
                member.role_id = role_id
            await self.session.flush([member])
            await self.session.commit()
        await self.session.refresh(member)
        return member
