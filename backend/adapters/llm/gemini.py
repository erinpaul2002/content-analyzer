from typing import AsyncIterator
from google import genai
from .base import LLMAdapter
from config.settings import settings

class GeminiLLMAdapter(LLMAdapter):
    def __init__(self):
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = settings.llm_model

    async def generate(self,prompt:str)->str:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )
        return response.text
    
    async def stream(self,prompt:str)->AsyncIterator[str]:
        for chunk in self.client.models.generate_content_stream(
            model=self.model,
            contents=prompt
        ):
            yield chunk.text