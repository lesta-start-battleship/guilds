from abc import ABC, abstractmethod

class ConsumerBase(ABC):
    
    @abstractmethod
    async def listen(): ...