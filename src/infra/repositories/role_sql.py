from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from infra.db.models.guild import RoleORM, PermissionORM

from domain.entities.guild import Role
from domain.repositories.role_repo import RoleRepositoryBase

from services.converters.orm_to_domain import role_orm_to_domain


class SQLRoleRepository(RoleRepositoryBase):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, role_id: int):
        result = await self.session.execute(
            select(RoleORM).options(
                selectinload(RoleORM.permissions),
                selectinload(RoleORM.promote_roles),
                ).
            where(RoleORM.id == role_id)
        )
        
        role = result.scalar_one_or_none()
        return role_orm_to_domain(role) if role else None
    
    
    async def get_by_title(self, title: str):
        result = await self.session.execute(
            select(RoleORM).
            options(
                selectinload(RoleORM.permissions),
                selectinload(RoleORM.promote_roles)
            ).
            where(RoleORM.title == title)
            )
        
        role = result.scalar_one_or_none()
        return role_orm_to_domain(role) if role else None
    
    
    async def list_roles(self):
        result = await self.session.execute(
            select(RoleORM).
            options(
                selectinload(RoleORM.permissions),
                selectinload(RoleORM.promote_roles)
            )
        )
        
        roles = result.scalars().all()
        return [role_orm_to_domain(role) for role in roles]
    
    
    async def save(self, role: Role):
        result = await self.session.execute(
            select(RoleORM).where(RoleORM.id.in_(role.promote_roles))
        )
        promote_roles = result.scalars().all()
        
        result = await self.session.execute(select(PermissionORM))
        all_permissions = result.scalars().all()
        perm_map = {p.permission: p for p in all_permissions}

        permissions = [perm_map[p] for p in role.permissions if p in perm_map]
        
        existing = await self.session.get(RoleORM, role.id) if role.id else None
        if existing:
            existing.id = role.id
            existing.title=role.title
            existing.permissions=permissions
            existing.promote_roles=promote_roles
        else:
            role_orm = RoleORM(
                id=role.id,
                title=role.title,
                permissions=permissions,
                promote_roles=promote_roles
            )
            self.session.add(role_orm)
            
        await self.session.commit()
    
    
    async def create(self, role: Role):
        result = await self.session.execute(
            select(RoleORM).where(RoleORM.id.in_(role.promote_roles))
        )
        promote_roles = result.scalars().all()
        
        result = await self.session.execute(select(PermissionORM))
        all_permissions = result.scalars().all()
        perm_map = {p.permission: p for p in all_permissions}

        permissions = [perm_map[p] for p in role.permissions if p in perm_map]
        
        role_orm = RoleORM(
            title=role.title,
            permissions=permissions,
            promote_roles=promote_roles
        )
        self.session.add(role_orm)
        await self.session.commit()
        return role_orm_to_domain(role_orm) if role_orm else None
    
    
    async def delete(self, role_id: int):
        role_orm = await self.session.scalar(select(RoleORM).where(RoleORM.id == role_id))
        if role_orm:
            await self.session.delete(role_orm)
            await self.session.commit()
    
    
    async def exists_by_id(self, role_id: int) -> bool:
        result = await self.session.execute(
            select(RoleORM.id).where(RoleORM.id == role_id)
        )
        return result.scalar_one_or_none() is not None