from langgraph.graph import StateGraph,END
from langgraph.checkpoint.memory import MemorySaver
from .state import ChatState
from .nodes import (
    router_node,
    metadata_retriever_node,
    transcript_retriever_node,
    draft_generator_node,
    logger_node,
    enhancer_node,
    formatter_node,
)

def build_chat_graph():
    graph= StateGraph(ChatState)
    
    graph.add_node("router",router_node)
    graph.add_node("fetch_metadata",metadata_retriever_node)
    graph.add_node("search_transcripts",transcript_retriever_node)
    graph.add_node("draft_generator",draft_generator_node)
    graph.add_node("logger",logger_node)
    graph.add_node("enhancer",enhancer_node)
    graph.add_node("formatter",formatter_node)

    graph.set_entry_point("enhancer")

    graph.add_edge("enhancer","router")

    def route_decision(state:ChatState):
        route = state.get("route","both")
        if route == "metadata_only":
            return "fetch_metadata"
        elif route == "transcript_only":
            return "search_transcripts"
        else:
            return "both"
    
    graph.add_conditional_edges("router",route_decision,{
        "fetch_metadata":"fetch_metadata",
        "search_transcripts":"search_transcripts",
        "both":"fetch_metadata",
    })

    def after_metadata(state:ChatState):
        if state.get("route") == "metadata_only":
            return "draft_generator"
        return "search_transcripts"

    graph.add_conditional_edges("fetch_metadata",after_metadata,{
        "draft_generator":"draft_generator",
        "search_transcripts":"search_transcripts",
    })

    graph.add_edge("search_transcripts","draft_generator")
    graph.add_edge("draft_generator","formatter")
    graph.add_edge("formatter","logger")
    graph.add_edge("logger",END)

    memory =MemorySaver()
    return graph.compile(checkpointer=memory)