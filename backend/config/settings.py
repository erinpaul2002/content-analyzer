import os
from pathlib import Path
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()

@dataclass(frozen=True)
class Settings:
    youtube_api_key: str | None = os.getenv("YOUTUBE_API_KEY")
    youtube_url: str | None = os.getenv("YOUTUBE_URL")
    pinecone_api_key: str | None = os.getenv("PINECONE_API_KEY")
    pinecone_index_name: str | None = os.getenv("PINECONE_INDEX_NAME")
    tokenizer_model: str | None = os.getenv("TOKENIZER_MODEL")
    transcripts_directory: Path = Path(os.getenv("TRANSCRIPTS_DIRECTORY", "/tmp"))
    gemini_api_key:str | None = os.getenv("GEMINI_API_KEY")
    groq_api_key:str | None = os.getenv("GROQ_API_KEY")
    openrouter_api_key:str | None = os.getenv("OPENROUTER_API_KEY")
    llm_model:str | None = os.getenv("LLM_MODEL")
    llm_provider:str | None = os.getenv("LLM_PROVIDER")
    convex_db_cloud_url:str | None =os.getenv("NEXT_PUBLIC_CONVEX_URL")

    #Test mode variables
    testing_mode: bool = os.getenv("TESTING_MODE", "false").lower() == "true"
    test_video_a_url: str | None = os.getenv("TEST_VIDEO_A_URL")
    test_video_b_url: str | None = os.getenv("TEST_VIDEO_B_URL")
    test_namespace: str | None = os.getenv("TEST_NAMESPACE")
    test_session_id: str | None = os.getenv("TEST_SESSION_ID")
settings = Settings()