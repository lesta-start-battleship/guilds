from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models.guild import Permission

class PermissionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def get_by_id(self, permission_id: int) -> Optional[Permission]:
        result = await self.session.execute(
            select(Permission).
            where(Permission.id == permission_id)
            )
        
        return result.scalar_one_or_none()
    
    async def get_by_title(self, title: str) -> Optional[Permission]:
        result = await self.session.execute(
            select(Permission).
            where(Permission.permission == title)
            )
        
        return result.scalar_one_or_none()
    
    async def get_permissions(self) -> List[Permission]:
        result = await self.session.execute(
            select(Permission)
            )
        
        return result.scalars().all()