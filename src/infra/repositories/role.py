from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.infra.models.guild import Role

class RoleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    
    async def get_by_id(self, role_id: int) -> Optional[Role]:
        result = self.session.execute(
            select(Role).
            where(Role.id == role_id)
            )
        
        return result.scalar_one_or_none()
    
    
    async def get_by_title(self, title: str) -> Optional[Role]:
        result = self.session.execute(
            select(Role).
            where(Role.title == title)
            )
        
        return result.scalar_one_or_none()
    
    
    async def get_roles(self) -> Optional[List[Role]]:
        result = self.session.execute(
            select(Role)
            )
        
        return result.scalars().all()
    
    
    async def create(
        self,
        title: str,
        edit: Optional[bool],
        balance: Optional[bool],
        owner: Optional[bool]
        ) -> Optional[Role]:
        role = await self.get_by_title(title=title)
        if not role:
            role = Role(
                title=title,
                edit=edit,
                balance=balance,
                owner=owner
                )
            
            await self.session.add(role)
            await self.session.commit()
            return role
    
    
    async def edit(
        self,
        role_id: int,
        title: Optional[str],
        edit: Optional[bool],
        balance: Optional[bool],
        owner: Optional[bool] 
        ) -> Optional[Role]:
        role = await self.get_by_id(role_id=role_id)
        
        if role:
            if title:
                role.title = title
            if edit is not None:
                role.edit = edit
            if balance is not None:
                role.balance = balance
            if owner is not None:
                role.owner = owner
            
            await self.session.flush(role)
            await self.session.commit()
            return role
        
        
    async def delete(
        self,
        role_id: int
        ) -> bool:
        role = await self.get_by_id(role_id=role_id)
        
        if role:
            await self.session.delete(role)
            await self.session.commit()
            return True
        return False