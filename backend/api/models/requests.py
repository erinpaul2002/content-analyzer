from pydantic import BaseModel
from typing import Optional

class IngestRequest(BaseModel):
    url_a:str
    url_b:str
    session_id: Optional[str] = None

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ConfirmIngestRequest(BaseModel):
    session_id: str
