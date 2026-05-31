from typing import List, TypedDict
from utils.tokenizer import Chunk

class EmbeddableRecord(TypedDict):
    id:str
    chunk_text:str
    video_id:str
    start_time:float
    end_time:float
    session_id:str

def prepare_records_for_embedding(
    chunks:List[Chunk],
    video_id:str,
    session_id:str
) -> List[EmbeddableRecord]:
    
    records=[]
    for chunk in chunks:
        record: EmbeddableRecord = {
            "id": chunk[chunk_id],
            "chunk_text": chunk["text"],
            "video_id": video_id,
            "start_time": chunk["start"],
            "end_time": chunk["end"],
            "session_id": session_id
        }
        records.append(record)
    return records

   