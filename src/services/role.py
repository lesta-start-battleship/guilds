from typing import List

from repositories.role import RoleRepository
from repositories.permisson import PermissionRepository

from exceptions.role import RoleNotFoundException, RoleAlreadyExistException

from services.converters import role_orm_to_dto

from schemas.role import RoleRequest, RoleResponse

class RoleService:
    def __init__(self, role_repo: RoleRepository, permission_repo: PermissionRepository):
        self.role_repo = role_repo
        self.permission_repo = permission_repo
    
    
    async def get_role_by_id(self, role_id: int) -> RoleResponse:
        role = self.role_repo.get_by_id(role_id)
        
        if not role:
            raise RoleNotFoundException
        
        return role_orm_to_dto(role)
    
    
    async def get_role_by_title(self, title: str):
        role = self.role_repo.get_by_title(title)
        
        if not role:
            raise RoleNotFoundException
        
        return role_orm_to_dto(role)
    
    
    async def get_role_list(self) -> List[RoleResponse]:
        roles = self.role_repo.get_roles()
        return [role_orm_to_dto(role) for role in roles]
    
    
    async def create_role(self, role_req: RoleRequest) -> RoleResponse:
        if await self.role_repo.get_by_title(role_req.title):
            raise RoleAlreadyExistException
        
        all_permissions = await self.permission_repo.get_permissions()
        
        permissions = [p for p in all_permissions if p.permission in role_req.permissions]
        
        role = await self.role_repo.create(role_req.title, permissions)
        
        if not role:
            raise RoleNotFoundException
        
        return role_orm_to_dto(role)
    
    
    async def delete_role(self, role_id: int) -> None:
        role = self.role_repo.get_by_id(role_id)
        
        if not role:
            raise RoleNotFoundException
        
        await self.role_repo.delete(role_id)
    
    
    async def edit_role(self, role_id, role_req: RoleRequest) -> RoleResponse:
        if not await self.role_repo.get_by_id(role_id):
            raise RoleNotFoundException
        
        all_permissions = await self.permission_repo.get_permissions()
        
        permissions = [p for p in all_permissions if p.permission in role_req.permissions]
        
        role = await self.role_repo.edit(role_id, role_req.title, permissions)
        
        if not role:
            raise RoleNotFoundException
        
        return role_orm_to_dto(role)