import config
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from api.models.requests import ChatRequest
from chat.graph import build_chat_graph
from langchain_core.messages import HumanMessage

router = APIRouter()
chat_graph=build_chat_graph()

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
    config = {"configurable":{"thread_id":req.session_id}}
    input_state={
        "messages": [HumanMessage(content=req.message)],
        "session_id":req.session_id,
    }

    async def event_generator():
        async for event in chat_graph.astream_events(input_state,config=config,version="v2"):
            if event["event"] == "on_chat_model_stream":
                token=event["data"]["chunk"].content
                yield f"data:{token}\n\n"
        yield "data:[DONE]\n\n"

    return StreamingResponse(event_generator(),media_type="text/event-stream")
