from abc import ABC,abstractmethod
from typing import AsyncIterator

class LLMAdapter(ABC):
    @abstractmethod
    async def generate(self,prompt:str, stream_queue=None)->str:
        pass

    @abstractmethod
    async def stream(self,prompt:str)->AsyncIterator[str]:
        pass