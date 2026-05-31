from datetime import datetime
from typing import List,Optional
from pydantic import BaseModel

class VideoMetadata(BaseModel):
    title:Optional[str]=None
    creator:Optional[str]=None
    upload_date:Optional[datetime]=None
    duration:Optional[str]=None
    views:Optional[int]=None
    likes:Optional[int]=None
    comments:Optional[int]=None
    subscribercount:Optional[int]=None
    profile_url:Optional[str]=None
    thumbnail_url:Optional[str]=None
    hashtags:Optional[List[str]]=None

class TranscriptSegment(BaseModel):
    text:str
    start:float
    duration:float
    end:Optional[float]=None

class VideoData(BaseModel):
    video_id:str
    metadata:VideoMetadata
    transcript:List[TranscriptSegment]
    timestamp:Optional[datetime]=None

class Chunk(BaseModel):
    video_id:str
    chunk_id:str
    text:str
    start:float
    end:float
    segment_ids:List[int]
    token_count:int

class EmbeddableRecord(BaseModel):
    chunk_id:str
    video_id:str
    chunk_text:str
    start_time:float
    end_time:float
    session_id:str

class Segment(BaseModel):
    id: int
    text: str
    start: float
    duration: float
    end: float