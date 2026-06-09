from typing import TypedDict,Optional,Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class ChatState(TypedDict):
    session_id: str
    messages: Annotated[list[BaseMessage], add_messages]
    route: Optional[str]
    enhanced_question: Optional[str]
    metadata_context: Optional[dict]
    transcript_chunks: Optional[list[dict]]
    draft_answer: Optional[str]
    final_answer: Optional[str]
    citations: Optional[list[dict]]
    verification_passed: Optional[bool]
    verification_feedback: Optional[str]
    verification_attempts: Optional[int]