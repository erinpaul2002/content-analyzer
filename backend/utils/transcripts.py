import json
from datetime import datetime,timezone
from pathlib import Path
from config.settings import settings
import os
from domain.models import VideoMetadata,TranscriptSegment,VideoData

TRANSCRIPTS_DIR=settings.transcripts_directory

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

def as_video_data(raw: dict) -> VideoData:
    raw_transcript = raw.get('transcript', {})
    segments=[]
    for key in sorted(raw_transcript.keys(), key=lambda x: int(x)):
        item = raw_transcript[key]
        text=item.get("text","")
        start=item.get("start",0.0)
        duration=item.get("duration",0.0)
        end=item.get("end",start+duration)
        segments.append(TranscriptSegment(text=text,start=start,duration=duration,end=end))
    metadata=VideoMetadata(
        title=raw.get("metadata", {}).get("title"),
        creator=raw.get("metadata", {}).get("creator"),
        upload_date=raw.get("metadata", {}).get("upload_date"),
        duration=raw.get("metadata", {}).get("duration"),
        views=raw.get("metadata", {}).get("views"),
        likes=raw.get("metadata", {}).get("likes"),
        comments=raw.get("metadata", {}).get("comments"),
        subscribercount=raw.get("metadata", {}).get("subscribercount"),
        profile_url=raw.get("metadata", {}).get("profile_url"),
        thumbnail_url=raw.get("metadata", {}).get("thumbnail_url"),
        hashtags=raw.get("metadata", {}).get("hashtags")
    )
    return VideoData(
        video_id=raw.get("video_id"),
        metadata=metadata,
        transcript=segments,
        timestamp=datetime.fromisoformat(raw.get("timestamp")) if raw.get("timestamp") else None
    )