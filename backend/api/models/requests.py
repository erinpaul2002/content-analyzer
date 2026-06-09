from pydantic import BaseModel

class IngestRequest(BaseModel):
    url_a:str
    url_b:str

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ConfirmIngestRequest(BaseModel):
    session_id: str
