from typing import TypedDict,Optional,Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class ChatState(TypedDict):
    session_id:str
    messages:Annotated[list[BaseMessage],add_messages]
    route:str
    metadata_context:Optional[dict]
    transcript_chunks:Optional[list[dict]]
    final_answer:str
    citations:list[dict]