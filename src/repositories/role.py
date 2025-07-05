from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.models.guild import Permission, Role

class RoleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    
    async def get_by_id(self, role_id: int) -> Optional[Role]:
        result = await self.session.execute(
            select(Role).
            options(selectinload(Role.permissions)).
            where(Role.id == role_id)
            )
        
        return result.scalar_one_or_none()
    
    
    async def get_by_title(self, title: str) -> Optional[Role]:
        result = await self.session.execute(
            select(Role).
            options(selectinload(Role.permissions)).
            where(Role.title == title)
            )
        
        return result.scalar_one_or_none()
    
    
    async def get_roles(self) -> List[Role]:
        result = await self.session.execute(
            select(Role)
            )
        
        return result.scalars().all()
    
    
    async def create(
        self,
        title: str,
        permissions: Optional[List[Permission]]
        ) -> Optional[Role]:
        role = await self.get_by_title(title=title)
        if not role:
            role = Role(
                title=title
                )
            
            if permissions:
                role.permissions = permissions
            
            self.session.add(role)
            await self.session.commit()
            return role
    
    
    async def edit(
        self,
        role_id: int,
        title: Optional[str],
        permissions: Optional[List[Permission]]
        ) -> Optional[Role]:
        role = await self.get_by_id(role_id=role_id)
        
        if role:
            if title:
                role.title = title
            
            if permissions or permissions == []:
                role.permissions = permissions
            
            await self.session.flush([role])
            await self.session.commit()
            return role
    
    
    async def delete(
        self,
        role_id: int
        ) -> bool:
        role = await self.get_by_id(role_id=role_id)
        
        if role:
            self.session.delete(role)
            await self.session.commit()
            return True
        return False