from typing import Optional
from adapters.storage.base import TranscriptStorageAdapter
from config.settings import settings
from convex import ConvexClient
from datetime import datetime,timezone

class ConvexStorageAdapter(TranscriptStorageAdapter):
    def __init__(self):
        if not settings.convex_db_cloud_url:
            raise ValueError("Convex db cloud url is not set")
        self.client = ConvexClient(settings.convex_db_cloud_url)

    def save(self,video_id:str,payload:dict)->str:
        payload.setdefault("timestamp",datetime.now(timezone.utc).isoformat())
        self.client.mutation("actions:saveVideo",{
            "video_id":video_id,
            "payload":payload,
        })
        return video_id

    def load(self,video_id:str)-> Optional[dict]:
        result=self.client.query("actions:getVideo",{"video_id":video_id})
        if not result:
            return None
        return result

    def exists(self,video_id:str)->bool:
        return self.load(video_id) is not None

