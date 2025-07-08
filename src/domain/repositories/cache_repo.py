from abc import ABC, abstractmethod
from typing import Optional, List

from domain.entities.guild_request import GuildJoinRequest

class CacheRepositoryBase(ABC):
    
    @abstractmethod
    async def request_list_by_tag(self, tag: str) -> List[GuildJoinRequest]: ...
    
    @abstractmethod
    async def request_list_by_user_id(self, user_id: int) -> List[GuildJoinRequest]: ...
    
    @abstractmethod
    async def request_list_delete_by_user_id(self, user_id: int) -> None: ...
    
    @abstractmethod
    async def request_list_delete_by_guild_tag(self, tag: str) -> None: ...
    
    @abstractmethod
    async def get_request(self, tag: str, user_id: int) -> Optional[GuildJoinRequest]: ...
    
    @abstractmethod
    async def save(self, request: GuildJoinRequest) -> None: ...
    
    @abstractmethod
    async def create(self, request: GuildJoinRequest) -> Optional[GuildJoinRequest]: ...
    
    @abstractmethod
    async def delete(self, tag: str, user_id: int) -> None: ...
    
    @abstractmethod
    async def check_request(self, tag: str, user_id: int) -> bool: ...