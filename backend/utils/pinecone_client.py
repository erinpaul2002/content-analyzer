import os
from dotenv import load_dotenv
from pinecone import Pinecone
from typing import Optional

load_dotenv()

class PineconeHandler:

    def __init__ (self,api_key:Optional[str]=None, index_name:Optional[str]=None):
        self.api_key=api_key or os.getenv("PINECONE_API_KEY")
        self.index_name=index_name or os.getenv("PINECONE_INDEX_NAME")
        if not self.api_key:
            raise RuntimeError("Pinecone api key not set")
        self._client:Optional[Pinecone]=None

    def get_client(self) -> Pinecone:
        if self._client is not None:
            return self._client
        kwargs={
            "api_key":self.api_key,
        }
        try:
            self._client=Pinecone(**kwargs)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Pinecone client: {e}")
        return self._client

    def get_index(self,index_name:Optional[str]=None):
        index_name=index_name or self.index_name
        if not index_name:
            raise RuntimeError("Pinecone index name not set")
        client = self.get_client()
        try:
            return client.Index(index_name)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Pinecone index: {e}")

    def upsert_vectors(self,vectors,namespace:str| None = None):
        index=self.get_index()
        try:
            if namespace:
                return index.upsert(vectors=vectors,namespace=namespace)
            raise RuntimeError("Namespace is required for upserting vectors")
        except Exception as e:
            raise RuntimeError(f"Failed to upsert vectors: {e}")    