from abc import ABC, abstractmethod

class ProducerBase(ABC):
    
    @abstractmethod
    def publish_guild_created(self, guild_id: int, guild_tag: str, owner_id: int): ...
    
    @abstractmethod
    def publish_guild_member_count_changed(self, guild_id: int, member_id: int, members_count: int): ...
    
    @abstractmethod
    def publish_guild_deleted(self, guild_id: int): ...