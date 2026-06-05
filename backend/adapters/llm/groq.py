from typing import AsyncIterator
from groq import AsyncGroq
from .base import LLMAdapter
from config.settings import settings

class GroqLLMAdapter(LLMAdapter):
    def __init__(self):
        self.client = AsyncGroq(api_key=settings.groq_api_key)
        self.model = settings.llm_model

    async def generate(self,prompt:str)->str:
        response = await self.client.chat.completions.create(
            messages=[{"role":"user","content":prompt}],
            model=self.model,
        )
        return response.choices[0].message.content

    async def stream(self,prompt:str)->AsyncIterator[str]:
        stream = await self.client.chat.completions.create(
            messages=[{"role":"user","content":prompt}],
            model=self.model,
            stream=True
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content