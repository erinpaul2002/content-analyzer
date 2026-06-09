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
) -> None:
    src_adapter=YoutubeVideoSourceAdapter()
    storage_adapter=ConvexStorageAdapter()
    print(f"Pipeline Started for URL: {url}")

    video_id=src_adapter.get_video_id(url)
    if not video_id:
        raise ValueError(f"Invalid Youtube URL: {url}")
    
    # Check if we already have it in Convex (Caching)
    existing_data = None
    if storage_adapter.exists(video_id):
        try:
            existing_data = storage_adapter.load(video_id)
        except Exception:
            pass

    if existing_data and "transcript" in existing_data and "metadata" in existing_data:
        print("Using cached transcript and metadata from storage")
    else:
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


def embed_session_videos(session_id: str) -> int:
    storage_adapter = ConvexStorageAdapter()
    session = storage_adapter.client.query("actions:getSession", {"session_id": session_id})
    if not session or "video_ids" not in session:
        raise ValueError(f"Session not found or has no videos: {session_id}")

    total_records = 0
    records = []
    for video_id in session["video_ids"]:
        video_data = storage_adapter.load(video_id)
        if not video_data or "transcript" not in video_data:
            print(f"Missing transcript for video {video_id}")
            continue

        raw_transcript = video_data["transcript"]
        segments = normalize_segments(raw_transcript)
        chunks = chunk_segments(video_id, segments)
        
        video_records = prepare_records_for_embedding(chunks, session_id)
        records.extend(video_records)

    if records:
        from adapters.vector_db.pinecone_adapter import PineconeVectorDBAdapter
        from config.settings import settings
        
        db_adapter = PineconeVectorDBAdapter()
        target_namespace = session_id if not settings.testing_mode else settings.test_namespace
        db_adapter.upsert(records=records, namespace=target_namespace)
        total_records = len(records)
        print(f"Upserted {total_records} records for session {session_id}")

    return total_records