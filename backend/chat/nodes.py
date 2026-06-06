import json
from pathlib import Path
from typing import Any
import re
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from .state import ChatState
from .prompts import ROUTER_PROMPT,SYSTEM_PROMPT,ENHANCER_PROMPT,FORMATTER_PROMPT
from adapters.llm.factory import GetLLMAdapter
from adapters.vector_db.pinecone_adapter import PineconeVectorDBAdapter
from adapters.storage.convex_storage import ConvexStorageAdapter
from config.settings import settings
from datetime import datetime

MAX_METADATA_TAGS = 8
MAX_CHUNK_CHARS = 4000
MAX_HISTORY_MESSAGES = 6


def _truncate_text(value: Any, max_chars: int) -> str:
    text = "" if value is None else str(value)
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def _compact_metadata(metadata: dict) -> dict:
    tags = metadata.get("hashtags")
    if not isinstance(tags, list):
        tags = []

    return {
        "title": metadata.get("title"),
        "creator": metadata.get("creator"),
        "views": metadata.get("views"),
        "likes": metadata.get("likes"),
        "comments": metadata.get("comments"),
        "engagement_rate": metadata.get("engagement_rate"),
        "subscriber_count": metadata.get("subscribercount") or metadata.get("subscriber_count"),
        "upload_date": metadata.get("upload_date"),
        "duration": metadata.get("duration"),
        "hashtags": tags[:MAX_METADATA_TAGS],
    }


def _format_recent_messages(messages: list) -> list[str]:
    recent_messages = messages[-MAX_HISTORY_MESSAGES:]
    formatted = []

    for msg in recent_messages:
        role = "User" if isinstance(msg, HumanMessage) else "Assistant"
        formatted.append(f"{role}: {_truncate_text(msg.content, 1200)}")

    return formatted

async def router_node(state:ChatState, config: RunnableConfig)->dict:
    question=state.get("enhanced_question") or state["messages"][-1].content

    llm=GetLLMAdapter()
    
    stream_queue = config.get("configurable", {}).get("stream_queue")

    prompt=ROUTER_PROMPT.format(question=question)
    response = await llm.generate(prompt, stream_queue=stream_queue)

    route=response.strip().lower()
    if route not in ["metadata_only","transcript_only","both"]:
        route = "both"
    return {"route":route}

def metadata_retriever_node(state:ChatState)->dict:
    """
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
                metadata_context[video_id]=_compact_metadata(video_data.get("metadata",{}))
    return {"metadata_context":metadata_context}
    """
    session_id=state["session_id"]
    storage_adapter = ConvexStorageAdapter()
    
    session = storage_adapter.client.query("actions:getSession", {"session_id": session_id})
    if not session:
        return {"metadata_context":{}}
    
    metadata_context={}
    for video_id in session.get("video_ids",[]):
        video_data = storage_adapter.load(video_id)
        if video_data:
            metadata_context[video_id]=_compact_metadata(video_data.get("metadata",{}))
            
    return {"metadata_context":metadata_context}
    
def transcript_retriever_node(state:ChatState)->dict:
    db=PineconeVectorDBAdapter()
    question=state.get("enhanced_question") or state["messages"][-1].content
    target_namespace=settings.test_namespace if settings.testing_mode and state.get("session_id") == settings.test_session_id else state.get("session_id")
    hits=db.search(query_text=question,namespace=target_namespace,top_k=5)
    return {"transcript_chunks":hits}

async def generator_node(state:ChatState, config: RunnableConfig)->dict:
    llm=GetLLMAdapter()

    context_parts=[]
    if state.get("metadata_context"):
        context_parts.append("METADATA:")
        context_parts.append(json.dumps(state["metadata_context"], separators=(",", ":")))
    
    if state.get("transcript_chunks"):
        context_parts.append("TRANSCRIPT_CHUNKS:")
        for chunk in state["transcript_chunks"]:
            chunk_text=_truncate_text(chunk.get("chunk_text"), MAX_CHUNK_CHARS)
            chunk_str=f"Video:{chunk.get('video_id')} | Chunk ID: {chunk.get('chunk_id')} | [{chunk.get('start_time')}s - {chunk.get('end_time')}s]: {chunk_text}"
            context_parts.append(chunk_str)
    context_str="\n\n".join(context_parts)    
    final_system_prompt=SYSTEM_PROMPT+f"\n\nCONTEXT AVAILABLE:\n{context_str}"

    prompt_parts=[final_system_prompt]

    prompt_parts.extend(_format_recent_messages(state["messages"]))
        
    final_prompt="\n\n".join(prompt_parts)
    print(f"DEBUG: final_prompt length = {len(final_prompt)} chars")
    
    stream_queue = config.get("configurable", {}).get("stream_queue")
    
    response = ""
    if stream_queue:
        in_reasoning = False
        buffer = ""
        async for chunk in llm.stream(final_prompt):
            response += chunk
            buffer += chunk
            
            while buffer:
                if not in_reasoning:
                    lower_buf = buffer.lower()
                    start_reasoning = lower_buf.find("<reasoning>")
                    start_think = lower_buf.find("<think>")
                    
                    start_idx = -1
                    tag_len = 0
                    if start_reasoning != -1 and (start_think == -1 or start_reasoning < start_think):
                        start_idx = start_reasoning
                        tag_len = len("<reasoning>")
                    elif start_think != -1:
                        start_idx = start_think
                        tag_len = len("<think>")

                    if start_idx != -1:
                        if start_idx > 0:
                            await stream_queue.put({"type": "token", "content": buffer[:start_idx]})
                        in_reasoning = True
                        buffer = buffer[start_idx + tag_len:]
                    else:
                        partial = False
                        for target in ["<reasoning>", "<think>"]:
                            for i in range(1, len(target)):
                                if lower_buf.endswith(target[:i]):
                                    partial = True
                                    split_at = len(buffer) - i
                                    if split_at > 0:
                                        await stream_queue.put({"type": "token", "content": buffer[:split_at]})
                                    buffer = buffer[split_at:]
                                    break
                            if partial:
                                break
                        
                        if not partial:
                            await stream_queue.put({"type": "token", "content": buffer})
                            buffer = ""
                        else:
                            break
                else:
                    lower_buf = buffer.lower()
                    end_reasoning = lower_buf.find("</reasoning>")
                    end_think = lower_buf.find("</think>")
                    
                    end_idx = -1
                    end_len = 0
                    if end_reasoning != -1 and (end_think == -1 or end_reasoning < end_think):
                        end_idx = end_reasoning
                        end_len = len("</reasoning>")
                    elif end_think != -1:
                        end_idx = end_think
                        end_len = len("</think>")

                    if end_idx != -1:
                        in_reasoning = False
                        buffer = buffer[end_idx + end_len:]
                        buffer = buffer.lstrip()
                    else:
                        if len(buffer) > 15:
                            buffer = buffer[-15:]
                        break
        
        if buffer and not in_reasoning:
            await stream_queue.put({"type": "token", "content": buffer})
    else:
        response=await llm.generate(final_prompt)

    # Extract reasoning
    reasoning_match = re.search(r"<(?:reasoning|think)>(.*?)(?:</(?:reasoning|think)>|$)", response, re.DOTALL | re.IGNORECASE)
    reasoning = reasoning_match.group(1).strip() if reasoning_match else None
    
    # Clean final answer
    final_answer = re.sub(r"<(?:reasoning|think)>.*?(?:</(?:reasoning|think)>|$)", "", response, flags=re.DOTALL | re.IGNORECASE).strip()
    final_answer = re.sub(r"(?:###|\*\*)\s*Reasoning:?\s*(?:\*\*|)\s*$", "", final_answer, flags=re.IGNORECASE).strip()

    citations=state.get("transcript_chunks",[])
    
    if stream_queue:
        await stream_queue.put({
            "type": "metadata",
            "citations": citations,
            "reasoning": reasoning
        })

    return {
            "messages": [AIMessage(content=final_answer)],
            "final_answer": final_answer,
            "reasoning": reasoning,
            "citations":citations
    }
    

def logger_node(state:ChatState)->dict:
    """
    session_id=state.get("session_id","unknown_session")
    log_dir=Path("data/logs")
    log_dir.mkdir(parents=True,exist_ok=True)
    log_path=log_dir/f"session_{session_id}.json"
    
    # Try to load existing log
    if log_path.exists():
        with open(log_path, "r", encoding="utf-8") as f:
            try:
                log_data = json.load(f)
            except json.JSONDecodeError:
                log_data = {"session_id": session_id, "turns": []}
    else:
        log_data = {"session_id": session_id, "turns": []}
        
    # Get user's question from history
    user_question = state["messages"][-2].content if len(state.get("messages", [])) >= 2 else "unknown"

    turn_data = {
        "timestamp": datetime.now().isoformat(),
        "question": user_question,
        "route": state.get("route"),
        "metadata_context": state.get("metadata_context"),
        "transcript_chunks_retrieved": state.get("transcript_chunks"),
        "reasoning": state.get("reasoning"),
        "final_answer": state.get("final_answer")
    }
    
    log_data["turns"].append(turn_data)

    with open(log_path,"w",encoding="utf-8") as f:
        json.dump(log_data,f,indent=4)

    print(f"\n[DEBUG] Session trace appended to:{log_path}")
    return {}
    """
    session_id=state.get("session_id","unknown_session")
    storage_adapter = ConvexStorageAdapter()
    
    log_data = storage_adapter.client.query("actions:getLog", {"session_id": session_id})
    if not log_data:
        log_data = {"session_id": session_id, "turns": []}
        
    # Get user's question from history
    user_question = state["messages"][-2].content if len(state.get("messages", [])) >= 2 else "unknown"
    turn_data = {
        "timestamp": datetime.now().isoformat(),
        "question": user_question,
        "route": state.get("route"),
        "metadata_context": state.get("metadata_context"),
        "transcript_chunks_retrieved": state.get("transcript_chunks"),
        "reasoning": state.get("reasoning"),
        "final_answer": state.get("final_answer")
    }
    
    log_data["turns"].append(turn_data)
    storage_adapter.client.mutation("actions:saveLog", {
        "session_id": session_id,
        "turns": log_data["turns"]
    })
    print(f"\n[DEBUG] Session trace appended to Convex for: {session_id}")
    return {}

async def enhancer_node(state:ChatState,config:RunnableConfig)->dict:
    question=state["messages"][-1].content
    llm=GetLLMAdapter()
    prompt=ENHANCER_PROMPT.format(question=question)
    response=await llm.generate(prompt)
    enhanced_question=response.strip()
    return {"enhanced_question":enhanced_question}


async def draft_generator_node(state:ChatState,config:RunnableConfig)->dict:
    llm=GetLLMAdapter()
    
    context_parts=[]
    if state.get("metadata_context"):
        context_parts.append("METADATA:")
        context_parts.append(json.dumps(state["metadata_context"],separators=(",",":")))

    if state.get("transcript_chunks"):
        context_parts.append("TRANSCRIPTS_CHUNKS:")
        for chunk in state["transcript_chunks"]:
            chunk_text=_truncate_text(chunk.get("chunk_text"),MAX_CHUNK_CHARS)
            chunk_str=f"Video:{chunk.get('video_id')} | Chunk ID: {chunk.get('chunk_id')} | [{chunk.get('start_time')}s - {chunk.get('end_time')}s]: {chunk_text}"
            context_parts.append(chunk_str)
    
    context_str="\n\n".join(context_parts)
    final_system_prompt=SYSTEM_PROMPT+f"\n\nCONTEXT AVAILABLE:\n{context_str}"

    prompt_parts=[final_system_prompt]
    prompt_parts.extend(_format_recent_messages(state["messages"]))
    final_prompt="\n\n".join(prompt_parts)

    response=await llm.generate(final_prompt)

    reasoning_match = re.search(r"<(?:reasoning|think)>(.*?)(?:</(?:reasoning|think)>|$)", response, re.DOTALL | re.IGNORECASE)
    reasoning = reasoning_match.group(1).strip() if reasoning_match else None
    
    citations = state.get("transcript_chunks", [])
    

    stream_queue = config.get("configurable", {}).get("stream_queue")
    if stream_queue:
        await stream_queue.put({
            "type": "metadata",
            "citations": citations,
            "reasoning": reasoning
        })
    return {
        "draft_answer": response,
        "reasoning": reasoning,
        "citations": citations
    }

async def formatter_node(state:ChatState,config:RunnableConfig)->dict:
    llm=GetLLMAdapter()
    draft=state.get("draft_answer","")
    prompt=FORMATTER_PROMPT.format(draft=draft)
    stream_queue=config.get("configurable",{}).get("stream_queue")

    response=""
    if stream_queue:
        async for chunk in llm.stream(prompt):
            response += chunk
            await stream_queue.put({"type": "token", "content": chunk})
    else:
        response = await llm.generate(prompt)
        
    return {
        "messages": [AIMessage(content=response)],
        "final_answer": response
    }
    