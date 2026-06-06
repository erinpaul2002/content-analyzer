from typing import List
from adapters.video_source.youtube import YoutubeVideoSourceAdapter
from adapters.storage.convex_storage import ConvexStorageAdapter
from processors.text_processor import normalize_segments
from processors.chunker import chunk_segments
from embeddings.record_formatter import prepare_records_for_embedding
from domain.models import EmbeddableRecord

def process_youtube_video(
    url:str,
    session_id:str
) -> List[EmbeddableRecord]:
    src_adapter=YoutubeVideoSourceAdapter()
    storage_adapter=ConvexStorageAdapter()
    print(f"Pipeline Started for URL: {url}")

    video_id=src_adapter.get_video_id(url)
    if not video_id:
        raise ValueError(f"Invalid Youtube URL: {url}")
    
    video_details=src_adapter.get_video_details(video_id)
    raw_transcript=src_adapter.get_video_transcript(video_id)
    if not raw_transcript:
        raise ValueError(f"Transcript not found for video: {video_id}")
    
    payload={
        "video_id":video_id,
        "metadata":video_details,
        "transcript":raw_transcript,
    }

    storage_adapter.save(video_id,payload)

    print("Transcript extracted and saved")

    segments=normalize_segments(raw_transcript)
    chunks=chunk_segments(video_id,segments)

    print("Segments chunked")

    records=prepare_records_for_embedding(chunks,session_id)

    print("Records prepared for embedding")

    return records