from config.settings import settings
from .base import LLMAdapter
from .gemini import GeminiLLMAdapter
from .groq import GroqLLMAdapter

def GetLLMAdapter() -> LLMAdapter:
    provider = settings.llm_provider.lower()
    if provider == "gemini":
        return GeminiLLMAdapter()
    elif provider == "groq":
        return GroqLLMAdapter()
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")