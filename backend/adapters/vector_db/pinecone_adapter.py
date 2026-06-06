from pinecone import Pinecone
from typing import List, Optional
from config.settings import settings
from domain.models import EmbeddableRecord

class PineconeVectorDBAdapter:
    def __init__(self, api_key: Optional[str] = None, index_name: Optional[str] = None):
        self.api_key = api_key or settings.pinecone_api_key
        self.index_name = index_name or settings.pinecone_index_name
        
        if not self.api_key or not self.index_name:
            raise RuntimeError("Pinecone API key and Index Name must be set in settings.")
            
        self.client = Pinecone(api_key=self.api_key)
        self.index = self.client.Index(self.index_name)

    def upsert(self, records: List[EmbeddableRecord], namespace: str) -> dict:
        pinecone_records = []
        for rec in records:
            pinecone_records.append({
                "_id": rec.chunk_id,
                "chunk_text": rec.chunk_text,
                "video_id": rec.video_id,
                "start_time": rec.start_time,
                "end_time": rec.end_time,
                "session_id": rec.session_id
            })

        print(f"Upserting {len(pinecone_records)} records to Pinecone namespace: '{namespace}'...")
        
        try:
            return self.index.upsert_records(
                namespace=namespace,
                records=pinecone_records
            )
        except Exception as e:
            raise RuntimeError(f"Failed to upsert records to Pinecone: {e}")


    def search(self,query_text:str,namespace:str,top_k:int=5)->list[dict]:
        response = self.index.search_records(
            namespace=namespace,
            top_k=top_k,
            inputs={"text":query_text},
            fields=["chunk_text","video_id","start_time","end_time","session_id"]
        )

        hits=[]
        for hit in response.result.hits:
            hits.append({
                "chunk_id":hit.id,
                "score":hit.score,
                **hit.fields
            })
        return hits

    def delete_namespace(self, namespace: str):
        try:
            self.index.delete(delete_all=True, namespace=namespace)
            print(f"Deleted Pinecone namespace: '{namespace}'")
        except Exception as e:
            print(f"Failed to delete Pinecone namespace '{namespace}': {e}")
            raise RuntimeError(f"Failed to delete Pinecone namespace: {e}")
