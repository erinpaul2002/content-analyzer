import json
from pathlib import Path
from langchain_core.messages import SystemMessage,HumanMessage
from .state import ChatState
from .prompts import ROUTER_PROMPT,SYSTEM_PROMPT
from adapters.llm.factory import GetLLMAdapter
from adapters.vector_db.pinecone_adapter import PineconeVectorDBAdapter
from config.settings import settings

async def router_node(state:ChatState)->dict:
    question=state["messages"][-1].content
    llm=GetLLMAdapter()

    prompt=ROUTER_PROMPT.format(question=question)
    response = await llm.generate(prompt)

    route=response.strip().lower()
    if route not in ["metadata_only","transcript_only","both"]:
        route = "both"
    return {"route":route}

def metadata_retriever_node(state:ChatState)->dict:
    session_id=state["session_id"]
    manifest_path=Path("data/sessions")/f"session_{session_id}.json"

    if not manifest_path.exists():
        return {"metadata_context":{}}
    
    with open(manifest_path,"r",encoding="utf-8") as f:
        manifest=json.load(f)
    metadata_context={}

    for video_id in manifest.get("video_ids",[]):
        video_json_path=settings.transcripts_directory/f"{video_id}.json"
        if video_json_path.exists():
            with open(video_json_path,"r",encoding="utf-8") as f:
                video_data=json.load(f)
                metadata_context[video_id]=video_data.get("metadata",{})
    return {"metadata_context":metadata_context}

def transcript_retriever_node(state:ChatState)->dict:
    db=PineconeVectorDBAdapter()
    question=state["messages"][-1].content
    hits=db.search(query_text=question,namespace=state["session_id"],top_k=5)
    return {"transcript_chunks":hits}

async def generator_node(state:ChatState)->dict:
    llm=GetLLMAdapter()

    context_parts=[]
    if state.get("metadata_context"):
        context_parts.append("METADATA:")
        context_parts.append(json.dumps(state["metadata_context"],indent=2))
    
    if state.get("transcript_chunks"):
        context_parts.append("TRANSCRIPT_CHUNKS:")
        for chunk in state["transcript_chunks"]:
            chunk_str=f"Video:{chunk.get('video_id')} | Chunk ID: {chunk.get('chunk_id')} | [{chunk.get('start_time')}s - {chunk.get('end_time')}s]: {chunk.get('chunk_text')}"
            context_parts.append(chunk_str)
    context_str="\n\n".join(context_parts)    
    final_system_prompt=SYSTEM_PROMPT+f"\n\nCONTEXT AVAILABLE:\n{context_str}"

    prompt_parts=[final_system_prompt]

    for msg in state["messages"]:
        role = "User" if isinstance(msg,HumanMessage) else "Assistant"
        prompt_parts.append(f"{role}:{msg.content}")
        
    final_prompt="\n\n".join(prompt_parts)
    response=await llm.generate(final_prompt)

    citations=state.get("transcript_chunks",[])

    return {
            "final_answer":response.strip(),
            "citations":citations
    }
    

        
        