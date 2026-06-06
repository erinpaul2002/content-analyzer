from multiprocessing import context
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from api.models.requests import ChatRequest
from chat.graph import build_chat_graph
from langchain_core.messages import HumanMessage,AIMessage
import asyncio
import json
from pathlib import Path
from adapters.storage.convex_storage import ConvexStorageAdapter


router = APIRouter()
chat_graph=build_chat_graph()


def _format_sse_data(data: str) -> str:
    lines = data.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    return "".join(f"data: {line}\n" for line in lines) + "\n"


def _chunk_text(text: str, size: int = 320):
    for index in range(0, len(text), size):
        yield text[index:index + size]

@router.post("")
async def chat(req:ChatRequest):
    config = {"configurable":{"thread_id":req.session_id}}
    input_state={
        "messages":[HumanMessage(content=req.message)],
        "session_id":req.session_id,
    }
    result=await chat_graph.ainvoke(input_state,config=config)
    return {
        "answer":result["final_answer"],
        "citations": result["citations"],
    }
@router.post("/stream")
async def chat_stream(req:ChatRequest):
    queue = asyncio.Queue()
    config = {"configurable":{"thread_id":req.session_id, "stream_queue": queue}}
    
    current_state=chat_graph.get_state(config=config)
    messages=[]
    if not current_state.values.get("messages"):
        """
        log_path=Path("data/logs")/f"session_{req.session_id}.json"
        if log_path.exists():
            with open(log_path,"r")as f:
                log_data=json.load(f)
                for turn in log_data.get("turns",[]):
                    if turn.get("question") and turn.get("question") != "unknown":
                        messages.append(HumanMessage(content=turn["question"]))
                    if turn.get("final_answer"):
                        messages.append(AIMessage(content=turn["final_answer"]))
        """
        storage_adapter = ConvexStorageAdapter()
        log_data = storage_adapter.client.query("actions:getLog", {"session_id": req.session_id})
        if log_data and log_data.get("turns"):
            for turn in log_data["turns"]:
                if turn.get("question") and turn.get("question") != "unknown":
                    messages.append(HumanMessage(content=turn["question"]))
                if turn.get("final_answer"):
                    messages.append(AIMessage(content=turn["final_answer"]))
    messages.append(HumanMessage(content=req.message))
    input_state={
        "messages": messages,
        "session_id":req.session_id,
    }

    async def event_generator():
        task = asyncio.create_task(chat_graph.ainvoke(input_state,config=config))
        try:
            while True:
                get_task = asyncio.create_task(queue.get())
                done, pending = await asyncio.wait(
                    [get_task, task],
                    return_when=asyncio.FIRST_COMPLETED
                )

                if get_task in done:
                    item = get_task.result()
                    if item["type"] == "done":
                        break
                    elif item["type"] == "token":
                        yield _format_sse_data(item["content"])
                    elif item["type"] == "metadata":
                        data = json.dumps(item)
                        yield f"event: metadata\n{_format_sse_data(data)}"
                else:
                    get_task.cancel()
                    if task.exception():
                        raise task.exception()
                    if queue.empty():
                        break
            yield "data:[DONE]\n\n"
        except Exception as e:
            print(f"Error in stream: {e}")
            yield _format_sse_data(f"Sorry, an error occurred: {str(e)}")
            yield "data:[DONE]\n\n"
        finally:
            if not task.done():
                task.cancel()

    return StreamingResponse(event_generator(),media_type="text/event-stream")
