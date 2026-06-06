from typing import AsyncIterator
import openai
from openai import AsyncOpenAI
from .base import LLMAdapter
from config.settings import settings

class OpenRouterLLMAdapter(LLMAdapter):
    def __init__(self):
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.openrouter_api_key,
        )
        self.model = settings.llm_model

    async def generate(self, prompt: str, stream_queue=None) -> str:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await self.client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=self.model,
                    max_tokens=4096,
                )
                content = response.choices[0].message.content
                return content if content is not None else ""
            except openai.RateLimitError as e:
                if attempt == max_retries - 1:
                    raise
                # Extract retry_after_seconds from the error if available, else default to 30
                try:
                    retry_after = e.response.json().get('error', {}).get('metadata', {}).get('retry_after_seconds', 30)
                except Exception:
                    retry_after = 30
                import asyncio
                print(f"[OpenRouter] Rate limited. Retrying after {retry_after} seconds...")
                print(f"[DEBUG] stream_queue is: {stream_queue}")
                if stream_queue:
                    print("[DEBUG] Putting message into stream_queue")
                    await stream_queue.put({"type": "token", "content": f"\n\n*[System: Processing hit API rate limit. Waiting {retry_after} seconds before continuing...]*\n\n"})
                await asyncio.sleep(retry_after)

    async def stream(self, prompt: str) -> AsyncIterator[str]:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                stream = await self.client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=self.model,
                    max_tokens=4096,
                    stream=True
                )
                async for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        yield chunk.choices[0].delta.content
                return
            except openai.RateLimitError as e:
                if attempt == max_retries - 1:
                    raise
                try:
                    retry_after = e.response.json().get('error', {}).get('metadata', {}).get('retry_after_seconds', 30)
                except Exception:
                    retry_after = 30
                import asyncio
                print(f"[OpenRouter Stream] Rate limited. Retrying after {retry_after} seconds...")
                yield f"\n\n*[System: API rate limit reached. Waiting {retry_after} seconds before retrying...]*\n\n"
                await asyncio.sleep(retry_after)
