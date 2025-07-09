from abc import ABC, abstractmethod
from typing import Optional, List, Tuple

from domain.entities.guild import Guild

class GuildRepositoryBase(ABC):
    
    @abstractmethod
    async def get_by_id(self, guild_id: int) -> Optional[Guild]: ...
    
    @abstractmethod
    async def get_by_tag(self, tag: str) -> Optional[Guild]: ...
    
    @abstractmethod
    async def get_by_owner_id(self, owner_id: int) -> Optional[Guild]: ...
    
    @abstractmethod
    async def list_guilds(self, offset: int = 0, limit: int = 10) -> Tuple[List[Guild], int]: ...
    
    @abstractmethod
    async def save(self, guild: Guild) -> None: ...
    
    @abstractmethod
    async def create(self, guild: Guild) -> Optional[Guild]: ...
    
    @abstractmethod
    async def delete(self, guild_tag: str) -> None: ...
    
    @abstractmethod
    async def exists_by_tag(self, tag: str) -> bool: ...