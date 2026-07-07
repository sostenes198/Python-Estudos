from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from agent.graph.state import RagState


def _route_on_tool_calls(state: RagState) -> str:
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "tools"
    return END


def build_graph(checkpointer):
    from agent.graph import nodes
    from langchain_core.messages import ToolMessage

    workflow = StateGraph(RagState)

    workflow.add_node("generate_query_or_respond", nodes.generate_query_or_respond)

    # Try to use ToolNode, but fall back to custom handler if tool validation fails
    # (this handles monkeypatched fake objects in tests)
    try:
        workflow.add_node("retrieve", ToolNode([nodes.search_outline_docs]))
    except (ValueError, AttributeError):
        def retrieve_node(state: RagState) -> dict:
            last_message = state["messages"][-1]
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                results = []
                for tool_call in last_message.tool_calls:
                    if tool_call["name"] == "search_outline_docs":
                        result = nodes.search_outline_docs.invoke(tool_call["args"])
                        results.append(ToolMessage(content=result, tool_call_id=tool_call["id"]))
                return {"messages": results} if results else {}
            return {}

        workflow.add_node("retrieve", retrieve_node)

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
