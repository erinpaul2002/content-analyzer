import uuid
from fastapi import APIRouter
from api.models.requests import IngestRequest, ConfirmIngestRequest
from domain.pipelines import process_youtube_video, embed_session_videos
from adapters.storage.convex_storage import ConvexStorageAdapter
from adapters.video_source.youtube import YoutubeVideoSourceAdapter
from config.settings import settings

router = APIRouter()

@router.post("/ingest")
def ingest_videos(req: IngestRequest):
    if settings.testing_mode:
        session_id=settings.test_session_id
        req.url_a=settings.test_video_a_url
        req.url_b=settings.test_video_b_url
    else:
        session_id=req.session_id if req.session_id else str(uuid.uuid4())
    
    src_adapter=YoutubeVideoSourceAdapter()
    storage_adapter=ConvexStorageAdapter()
    results=[]
    videos={}
    video_inputs=[("A",req.url_a),("B",req.url_b)]
    
    successful_video_ids = []
    labels = {}

    for label,url in video_inputs:
        try:
            video_id=src_adapter.get_video_id(url)
            if not video_id:
                raise ValueError(f"Invalid Youtube URL: {url}")
            
            process_youtube_video(url,session_id)
            status_msg="success (test mode)" if settings.testing_mode else "success"
                
            videos[label]=storage_adapter.load(video_id)
            results.append({
                "url":url,
                "status":status_msg
            })
            successful_video_ids.append(video_id)
            labels[video_id] = label
        except Exception as e:
            results.append({
                "url":url,
                "status":"error",
                "message":str(e)
            })

    session_manifest={
        "session_id":session_id,
        "video_ids":successful_video_ids,
        "labels":labels
    }

    storage_adapter.client.mutation("actions:createSession",session_manifest)

    return {
        "session_id":session_id,
        "results":results,
        "videos":videos
    }

@router.post("/confirm_ingest")
def confirm_ingest(req: ConfirmIngestRequest):
    try:
        total_records = embed_session_videos(req.session_id)
        return {
            "status": "success",
            "session_id": req.session_id,
            "upserted_count": total_records
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
