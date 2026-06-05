from langgraph.graph import StateGraph,END
from langgraph.checkpoint.memory import MemorySaver
from .state import ChatState
from .nodes import (
    router_node,metadata_retriever_node,transcript_retriever_node,generator_node
)

def build_chat_graph():
    graph= StateGraph(ChatState)
    
    graph.add_node("router",router_node)
    graph.add_node("fetch_metadata",metadata_retriever_node)
    graph.add_node("search_transcripts",transcript_retriever_node)
    graph.add_node("generate",generator_node)

    graph.set_entry_point("router")

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
            return "generate"
        return "search_transcripts"

    graph.add_conditional_edges("fetch_metadata",after_metadata,{
        "generate":"generate",
        "search_transcripts":"search_transcripts",
    })

    graph.add_edge("search_transcripts","generate")
    graph.add_edge("generate",END)

    memory =MemorySaver()
    return graph.compile(checkpointer=memory)