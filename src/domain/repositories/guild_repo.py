from abc import ABC, abstractmethod
from typing import Optional, List

from src.domain.models.guild import Guild

class GuildRepository(ABC):
    
    @abstractmethod
    async def get_by_id(self, guild_id: int) -> Optional[Guild]: ...
    
    @abstractmethod
    async def get_by_tag(self, tag: str) -> Optional[Guild]: ...
    
    @abstractmethod
    async def list_guilds(self, offset: int = 0, limit: int = 10) -> List[Guild]: ...
    
    @abstractmethod
    async def create(self, guild: Guild) -> Optional[Guild]: ...
    
    @abstractmethod
    async def delete(self, guild_id: int) -> None: ...
    
    @abstractmethod
    async def edit(self, guild_id: int, title: Optional[str], description: Optional[str]) -> Optional[Guild]: ...