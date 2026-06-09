from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from .state import ChatState
from .nodes import (
    state_clearer_node,
    router_node,
    metadata_retriever_node,
    transcript_retriever_node,
    draft_generator_node,
    verifier_node,
    logger_node,
    enhancer_node,
    formatter_node,
)

def build_chat_graph():
    graph = StateGraph(ChatState)

    graph.add_node("state_clearer", state_clearer_node)
    graph.add_node("router", router_node)
    graph.add_node("enhancer", enhancer_node)
    graph.add_node("fetch_metadata", metadata_retriever_node)
    graph.add_node("search_transcripts", transcript_retriever_node)
    graph.add_node("draft_generator", draft_generator_node)
    graph.add_node("verifier", verifier_node)
    graph.add_node("formatter", formatter_node)
    graph.add_node("logger", logger_node)

    graph.set_entry_point("state_clearer")
    graph.add_edge("state_clearer", "router")

    # Route on original question
    def route_decision(state: ChatState):
        route = state.get("route", "both")
        if route == "metadata_only":
            return "metadata_only"
        elif route == "transcript_only":
            return "transcript_only"
        else:
            return "both"

    graph.add_conditional_edges("router", route_decision, {
        "metadata_only": "fetch_metadata",
        "transcript_only": "enhancer",
        "both": "enhancer",
    })

    graph.add_edge("enhancer", "fetch_metadata")

    # After metadata, go to search or draft depending on route
    def after_metadata(state: ChatState):
        if state.get("route") == "metadata_only":
            return "draft_generator"
        return "search_transcripts"

    graph.add_conditional_edges("fetch_metadata", after_metadata, {
        "draft_generator": "draft_generator",
        "search_transcripts": "search_transcripts",
    })

    graph.add_edge("search_transcripts", "draft_generator")
    
    graph.add_edge("draft_generator", "verifier")

    def after_verifier(state: ChatState):
        if state.get("verification_passed", False) or state.get("verification_attempts", 0) >= 3:
            return "formatter"
        return "draft_generator"

    graph.add_conditional_edges("verifier", after_verifier, {
        "formatter": "formatter",
        "draft_generator": "draft_generator"
    })

    graph.add_edge("formatter", "logger")
    graph.add_edge("logger", END)

    memory = MemorySaver()
    return graph.compile(checkpointer=memory)