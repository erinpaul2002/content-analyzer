import uuid
from fastapi import APIRouter
import json
from pathlib import Path
from api.models.requests import IngestRequest
from domain.pipelines import process_youtube_video
#from adapters.storage.json_storage import JsonStorageAdapter
from adapters.storage.convex_storage import ConvexStorageAdapter
from adapters.vector_db.pinecone_adapter import PineconeVectorDBAdapter
from adapters.video_source.youtube import YoutubeVideoSourceAdapter
from config.settings import settings

router = APIRouter()

@router.post("/ingest")
def ingest_videos(req: IngestRequest):

    #Use Test variables if Test mode is active
    if settings.testing_mode:
        session_id=settings.test_session_id
        req.url_a=settings.test_video_a_url
        req.url_b=settings.test_video_b_url
    else:
        session_id=str(uuid.uuid4())
    
    db_adapter=PineconeVectorDBAdapter()
    src_adapter=YoutubeVideoSourceAdapter()
    #storage_adapter=JsonStorageAdapter()
    storage_adapter=ConvexStorageAdapter()
    results=[]
    videos={}
    video_inputs=[("A",req.url_a),("B",req.url_b)]
    for label,url in video_inputs:
        try:
            video_id=src_adapter.get_video_id(url)
            if not video_id:
                raise ValueError(f"Invalid Youtube URL: {url}")
            
            if settings.testing_mode and storage_adapter.exists(video_id):
                records=[]
                status_msg="success (test mode - skipped upsert)"
            else:
                records=process_youtube_video(url,session_id)
                target_namespace=session_id if not settings.testing_mode else settings.test_namespace
                db_adapter.upsert(records=records,namespace=target_namespace)
                status_msg="success (test mode - initially processed)" if settings.testing_mode else "success"
            videos[label]=storage_adapter.load(video_id)
            results.append({
                "url":url,
                "status":status_msg,
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

    # sessions_dir=Path("data/sessions")
    # sessions_dir.mkdir(parents=True,exist_ok=True)

    # with open(sessions_dir/f"session_{session_id}.json","w",encoding="utf-8") as f:
    #     json.dump(session_manifest,f)

    storage_adapter.client.mutation("actions:createSession",session_manifest)

    
    return {
        "session_id":session_id,
        "results":results,
        "videos":videos
    }
