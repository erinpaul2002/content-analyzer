import json
import os
from datetime import datetime,timezone
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

TRANSCRIPTS_DIR=os.getenv("TRANSCRIPTS_DIR")

def ensure_directory_exists(directory: str) -> Path:
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path

def save_transcript(data: dict) -> Path:
    transcripts_directory=ensure_directory_exists(TRANSCRIPTS_DIR)
    
    payload = {
        "video_id": data['video_id'],
        "transcript": data['transcript'],
        "metadata": {
            "title": data['title'],
            "creator": data['creator'],
            "upload_date": data['upload_date'],
            "duration": data['duration'],
            "views": data['views'],
            "likes": data['likes'],
            "comments": data['comments'],
            "subscribercount": data['subscribercount'],
            "profile_url": data['profile_url'],
            "thumbnail_url": data['thumbnail_url'],
            "hashtags": data['hashtags']
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    file_path = transcripts_directory / f"{data['video_id']}.json"
    temp_file_path = file_path.with_suffix('.json.tmp')
    with open(temp_file_path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    os.replace(temp_file_path, file_path)
    return file_path

def load_transcripts(video_id:str)-> dict | None:
    transcripts_directory=ensure_directory_exists(TRANSCRIPTS_DIR)
    file_path = transcripts_directory / f"{video_id}.json"
    if not file_path.exists():
        return None
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def transcript_exists(video_id:str) -> bool:
    transcripts_directory=ensure_directory_exists(TRANSCRIPTS_DIR)
    file_path = transcripts_directory / f"{video_id}.json"
    return file_path.exists()