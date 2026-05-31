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
    transcripts_directory: Path = Path(os.getenv("TRANSCRIPTS_DIRECTORY"))

settings = Settings()