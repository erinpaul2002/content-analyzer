import json
from pathlib import Path
from typing import Any
import re
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from .state import ChatState
from .prompts import ROUTER_PROMPT, SYSTEM_PROMPT, ENHANCER_PROMPT, FORMATTER_PROMPT, VERIFIER_PROMPT
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

def state_clearer_node(state: ChatState) -> dict:
    """Reset all ephemeral state at the start of every turn."""
    return {
        "metadata_context": None,
        "transcript_chunks": None,
        "draft_answer": None,
        "final_answer": None,
        "citations": None,
        "route": None,
        "enhanced_question": None,
        "verification_passed": None,
        "verification_feedback": None,
        "verification_attempts": 0,
    }

async def router_node(state: ChatState, config: RunnableConfig) -> dict:
    question = state["messages"][-1].content  # original, never enhanced
    llm = GetLLMAdapter()
    stream_queue = config.get("configurable", {}).get("stream_queue")
    prompt = ROUTER_PROMPT.format(question=question)
    response = await llm.generate(prompt, stream_queue=stream_queue)
    route = response.strip().lower()
    if route not in ["metadata_only", "transcript_only", "both"]:
        route = "both"
    return {"route": route}

def metadata_retriever_node(state: ChatState) -> dict:
    session_id = state["session_id"]
    storage_adapter = ConvexStorageAdapter()
    
    session = storage_adapter.client.query("actions:getSession", {"session_id": session_id})
    if not session:
        return {"metadata_context": {}}
    
    metadata_context = {}
    for video_id in session.get("video_ids", []):
        video_data = storage_adapter.load(video_id)
        if video_data:
            metadata_context[video_id] = _compact_metadata(video_data.get("metadata", {}))
            
    return {"metadata_context": metadata_context}

# ─── Video Detection ───
_STOPWORDS = {"the", "a", "an", "is", "it", "of", "in", "to", "and", "for", "on", "with", "this", "that", "about"}

def _extract_title_keywords(title: str) -> set[str]:
    """Extract meaningful keywords from a video title. No naive word>4 matching."""
    import re as _re
    # Remove punctuation, normalize
    words = _re.findall(r"[a-z0-9]+", title.lower())
    # Keep words > 3 chars, skip stopwords and generic terms
    return {w for w in words if len(w) > 3 and w not in _STOPWORDS}

def _detect_target_video(question: str, labels: dict, video_metadata: dict) -> str | None:
    """
    Detect if the user is asking about a specific video.
    """
    q_lower = question.lower()

    # 1. Check by label: "video a", "video b"
    for video_id, label in labels.items():
        if f"video {label.lower()}" in q_lower:
            return video_id

    # 2. Check by title and creator keywords
    best_match = None
    best_count = 0
    for video_id, meta in video_metadata.items():
        title = meta.get("title", "")
        creator = meta.get("creator", "")
        
        keywords = _extract_title_keywords(title)
        import re
        creator_words = {w for w in re.findall(r"[a-z0-9]+", creator.lower()) if len(w) > 3 and w not in _STOPWORDS}
        keywords.update(creator_words)
        
        match_count = sum(1 for kw in keywords if kw in q_lower)
        if match_count > best_count:
            best_count = match_count
            best_match = video_id

    # Require at least 1 keyword match
    if best_count >= 1:
        return best_match

    return None

def _interleave_hits(hits_per_video: dict[str, list[dict]], total: int = 5) -> list[dict]:
    """
    True round-robin interleaving with reserved slots.
    Produces: A1, B1, A2, B2, A3, ...
    Each video's hits are pre-sorted by score descending.
    """
    result = []
    iterators = {vid: iter(hits) for vid, hits in hits_per_video.items()}
    video_order = list(hits_per_video.keys())

    while len(result) < total:
        added_any = False
        for vid in video_order:
            if len(result) >= total:
                break
            try:
                result.append(next(iterators[vid]))
                added_any = True
            except StopIteration:
                continue
        if not added_any:
            break

    return result

def transcript_retriever_node(state: ChatState) -> dict:
    db = PineconeVectorDBAdapter()
    question = state.get("enhanced_question") or state["messages"][-1].content
    target_namespace = (
        settings.test_namespace
        if settings.testing_mode and state.get("session_id") == settings.test_session_id
        else state.get("session_id")
    )

    # Load session data from Convex for labels and video titles
    storage = ConvexStorageAdapter()
    session = storage.client.query("actions:getSession", {"session_id": state["session_id"]})
    labels = session.get("labels", {}) if session else {}
    video_ids = session.get("video_ids", []) if session else []

    video_metadata = state.get("metadata_context") or {}

    target_video_id = _detect_target_video(
        state["messages"][-1].content,  # original question for detection
        labels,
        video_metadata,
    )

    if target_video_id:
        # Single-video filtered search
        hits = db.search(
            query_text=question, namespace=target_namespace, top_k=5,
            filter={"video_id": {"$eq": target_video_id}},
        )
    elif len(video_ids) >= 2:
        # Balanced interleaved search — one query per video, round-robin merge
        hits_per_video = {}
        per_video_k = 3  # fetch 3 per video, interleave to 5
        for vid in video_ids:
            vid_hits = db.search(
                query_text=question, namespace=target_namespace,
                top_k=per_video_k,
                filter={"video_id": {"$eq": vid}},
            )
            hits_per_video[vid] = vid_hits
        hits = _interleave_hits(hits_per_video, total=5)
    else:
        # Fallback: unfiltered
        hits = db.search(query_text=question, namespace=target_namespace, top_k=5)

    return {"transcript_chunks": hits}

async def enhancer_node(state: ChatState, config: RunnableConfig) -> dict:
    question = state["messages"][-1].content
    llm = GetLLMAdapter()
    prompt = ENHANCER_PROMPT.format(question=question)
    response = await llm.generate(prompt)
    enhanced_question = response.strip()
    return {"enhanced_question": enhanced_question}

async def draft_generator_node(state: ChatState, config: RunnableConfig) -> dict:
    llm = GetLLMAdapter()

    context_parts = []
    if state.get("metadata_context"):
        context_parts.append("METADATA:")
        context_parts.append(json.dumps(state["metadata_context"], separators=(",", ":")))

    if state.get("transcript_chunks"):
        context_parts.append("TRANSCRIPT_CHUNKS:")
        for chunk in state["transcript_chunks"]:
            chunk_text = _truncate_text(chunk.get("chunk_text"), MAX_CHUNK_CHARS)
            chunk_str = (
                f"Video:{chunk.get('video_id')} | Chunk ID: {chunk.get('chunk_id')} "
                f"| [{chunk.get('start_time')}s - {chunk.get('end_time')}s]: {chunk_text}"
            )
            context_parts.append(chunk_str)

    context_str = "\n\n".join(context_parts)
    final_system_prompt = SYSTEM_PROMPT + f"\n\nCONTEXT AVAILABLE:\n{context_str}"
    
    if state.get("verification_feedback"):
        final_system_prompt += f"\n\nPREVIOUS ATTEMPT FAILED VERIFICATION. FEEDBACK TO FIX:\n{state['verification_feedback']}"

    prompt_parts = [final_system_prompt]
    prompt_parts.extend(_format_recent_messages(state["messages"]))
    final_prompt = "\n\n".join(prompt_parts)

    response = await llm.generate(final_prompt)

    # Defensive strip — model should not produce these, but remove if present
    clean_draft = re.sub(
        r"<(?:reasoning|think)>.*?(?:</(?:reasoning|think)>|$)",
        "", response, flags=re.DOTALL | re.IGNORECASE
    ).strip()

    citations = state.get("transcript_chunks") or []

    stream_queue = config.get("configurable", {}).get("stream_queue")
    if stream_queue and state.get("verification_attempts", 0) == 0:
        await stream_queue.put({
            "type": "metadata",
            "citations": citations,
        })

    return {
        "draft_answer": clean_draft,
        "citations": citations,
    }

async def verifier_node(state: ChatState, config: RunnableConfig) -> dict:
    llm = GetLLMAdapter()
    draft = state.get("draft_answer", "")
    question = state["messages"][-1].content
    prompt = VERIFIER_PROMPT.format(question=question, draft=draft)
    
    # We enforce JSON output but LLMs can sometimes wrap it in markdown.
    response = await llm.generate(prompt)
    
    # Try to parse JSON from the response
    passed = False
    feedback = ""
    try:
        # Strip markdown JSON fences if present
        import re
        json_match = re.search(r'\{.*\}', response.strip(), re.DOTALL)
        clean_json = json_match.group(0) if json_match else response.strip()
        parsed = json.loads(clean_json)
        passed = parsed.get("passed", False)
        feedback = parsed.get("feedback", "")
    except Exception as e:
        print(f"Error parsing verifier JSON: {e}")
        # If parsing fails, we could just assume it failed or passed. Let's assume it failed.
        feedback = "Failed to parse verification feedback."
        
    attempts = state.get("verification_attempts", 0) + 1
    
    return {
        "verification_passed": passed,
        "verification_feedback": feedback,
        "verification_attempts": attempts,
    }

async def formatter_node(state: ChatState, config: RunnableConfig) -> dict:
    llm = GetLLMAdapter()
    draft = state.get("draft_answer", "")
    prompt = FORMATTER_PROMPT.format(draft=draft)
    stream_queue = config.get("configurable", {}).get("stream_queue")

    response = ""
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

def logger_node(state: ChatState) -> dict:
    session_id = state.get("session_id", "unknown_session")
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
        "final_answer": state.get("final_answer"),
        "verification_attempts": state.get("verification_attempts"),
        "verification_feedback": state.get("verification_feedback")
    }
    
    log_data["turns"].append(turn_data)
    storage_adapter.client.mutation("actions:saveLog", {
        "session_id": session_id,
        "turns": log_data["turns"]
    })
    print(f"\n[DEBUG] Session trace appended to Convex for: {session_id}")
    return {}