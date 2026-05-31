from pathlib import Path
from typing import Optional
from adapters.storage.base import TranscriptStorageAdapter
from config.settings import settings
import json
import os
from datetime import datetime,timezone

TRANSCRIPTS_DIRECTORY = Path(settings.transcripts_directory)


class JsonStorageAdapter(TranscriptStorageAdapter):
    def __init__(self, directory: Optional[Path] = None):
        self.directory = directory or TRANSCRIPTS_DIRECTORY
        self.directory.mkdir(parents=True, exist_ok=True)
    
    def _path(self, video_id: str) -> Path:
        return self.directory / f"{video_id}.json"

    def save(self, video_id: str, payload: dict) -> str:
        file_path = self._path(video_id)
        tmp_file_path = file_path.with_suffix('.json.tmp')
        payload.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
        with open(tmp_file_path, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        os.replace(tmp_file_path, file_path)
        return str(file_path)

    def load(self, video_id: str) -> Optional[dict]:
        file_path = self._path(video_id)
        if not file_path.exists():
            return None
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def exists(self, video_id: str) -> bool:
        return self._path(video_id).exists()