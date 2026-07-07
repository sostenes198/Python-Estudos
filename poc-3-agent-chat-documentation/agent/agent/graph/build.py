from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from agent.graph import nodes
from agent.graph.state import RagState
from agent.retrieval.tools import search_outline_docs


def _route_on_tool_calls(state: RagState) -> str:
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "tools"
    return END


def build_graph(checkpointer):
    workflow = StateGraph(RagState)

    workflow.add_node("generate_query_or_respond", nodes.generate_query_or_respond)
    workflow.add_node("retrieve", ToolNode([search_outline_docs]))
    workflow.add_node("rewrite_question", nodes.rewrite_question)
    workflow.add_node("generate_answer", nodes.generate_answer)
    workflow.add_node("no_context_found", nodes.no_context_found)

    workflow.add_edge(START, "generate_query_or_respond")
    workflow.add_conditional_edges(
        "generate_query_or_respond",
        _route_on_tool_calls,
        {"tools": "retrieve", END: END},
    )
    workflow.add_conditional_edges("retrieve", nodes.grade_documents)
    workflow.add_edge("rewrite_question", "generate_query_or_respond")
    workflow.add_edge("generate_answer", END)
    workflow.add_edge("no_context_found", END)

    return workflow.compile(checkpointer=checkpointer)
