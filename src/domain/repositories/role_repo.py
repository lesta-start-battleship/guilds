from abc import ABC, abstractmethod
from typing import Optional, List

from domain.entities.guild import Role

class RoleRepositoryBase(ABC):
    
    @abstractmethod
    async def get_by_id(self, role_id: int) -> Optional[Role]: ...
    
    @abstractmethod
    async def get_by_title(self, title: str) -> Optional[Role]: ...
    
    @abstractmethod
    async def list_roles(self) -> List[Role]: ...
    
    @abstractmethod
    async def save(self, role: Role) -> None: ...
    
    @abstractmethod
    async def create(self, role: Role) -> Optional[Role]: ...
    
    @abstractmethod
    async def delete(self, role_id: int) -> None: ...
    
    @abstractmethod
    async def exists_by_id(self, role_id: int) -> bool: ...