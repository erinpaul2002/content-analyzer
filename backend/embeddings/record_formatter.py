from typing import List
from domain.models import EmbeddableRecord, Chunk

def prepare_records_for_embedding(
    chunks: List[Chunk],
    session_id: str
) -> List[EmbeddableRecord]:
    records = []
    for chunk in chunks:
        record = EmbeddableRecord(
            chunk_id=chunk.chunk_id,
            chunk_text=chunk.text,
            video_id=chunk.video_id,
            start_time=chunk.start,
            end_time=chunk.end,
            session_id=session_id
        )
        records.append(record)
    return records
