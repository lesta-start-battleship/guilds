from abc import ABC, abstractmethod
from typing import Optional, List, Tuple

from domain.entities.guild import Member

class MemberRepositoryBase(ABC):
    
    @abstractmethod
    async def get_by_id(self, guild_id: int) -> Optional[Member]: ...
    
    @abstractmethod
    async def list_members_by_guild_tag(self, guild_tag: str, offset: int = 0, limit: int = 10) -> Tuple[List[Member], int]: ...
    
    @abstractmethod
    async def list_members_by_guild_id(self, guild_id: int) -> List[Member]: ...
    
    @abstractmethod
    async def save(self, member: Member) -> None: ...
    
    @abstractmethod
    async def create(self, member: Member) -> Optional[Member]: ...
    
    @abstractmethod
    async def delete(self, user_id: int) -> None: ...
    
    @abstractmethod
    async def exists_by_id(self, user_id: int) -> bool: ...