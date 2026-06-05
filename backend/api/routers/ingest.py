from urllib import response
import uuid
from fastapi import APIRouter,HTTPException
import json
from pathlib import Path
from api.models.requests import IngestRequest
from domain.pipelines import process_youtube_video
from adapters.vector_db.pinecone_adapter import PineconeVectorDBAdapter
from adapters.video_source.youtube import YoutubeVideoSourceAdapter

router = APIRouter()

@router.post("/ingest")
def ingest_videos(req: IngestRequest):
    session_id = str(uuid.uuid4())
    db_adapter=PineconeVectorDBAdapter()
    src_adapter=YoutubeVideoSourceAdapter()
    results=[]
    for url in [req.url_a,req.url_b]:
        try:
            records=process_youtube_video(url,session_id)
            response = db_adapter.upsert(records=records,namespace=session_id)
            results.append({
                "url":url,
                "status":"success",
                "upserted_count":len(records)
            })
        except Exception as e:
            results.append({
                "url":url,
                "status":"error",
                "message":str(e)
            })
    video_id_a=src_adapter.get_video_id(req.url_a)
    video_id_b=src_adapter.get_video_id(req.url_b)
    session_manifest={
        "session_id":session_id,
        "video_ids":[video_id_a,video_id_b],
        "labels":{video_id_a:"A",video_id_b:"B"}
    }

    sessions_dir=Path("data/sessions")
    sessions_dir.mkdir(parents=True,exist_ok=True)

    with open(sessions_dir/f"session_{session_id}.json","w",encoding="utf-8") as f:
        json.dump(session_manifest,f)

    
    return {
        "session_id":session_id,
        "results":results
    }
