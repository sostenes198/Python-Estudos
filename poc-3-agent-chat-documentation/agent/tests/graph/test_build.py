from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.checkpoint.memory import InMemorySaver


def test_graph_happy_path_calls_tool_then_generates_answer(monkeypatch):
    from agent.graph import build, nodes
    from agent.retrieval import tools

    def fake_generate_query_or_respond(state):
        if len(state["messages"]) == 1:
            return {
                "messages": [
                    AIMessage(
                        content="",
                        tool_calls=[{"id": "1", "name": "search_outline_docs", "args": {"query": "billing"}}],
                    )
                ]
            }
        return {"messages": [AIMessage(content="should not reach here")]}

    monkeypatch.setattr(nodes, "generate_query_or_respond", fake_generate_query_or_respond)
    monkeypatch.setattr(
        tools,
        "hybrid_search",
        lambda query, team=None, k=5: [
            {"content": "Billing is monthly.", "source": "s", "owner": "Billing", "title": "t"}
        ],
    )
    monkeypatch.setattr(nodes, "grade_documents", lambda state: "generate_answer")
    monkeypatch.setattr(nodes, "generate_answer", lambda state: {"messages": [AIMessage(content="Billing is monthly.\n\nFontes:\n- Billing: s")]})

    graph = build.build_graph(InMemorySaver())
    result = graph.invoke(
        {"messages": [HumanMessage(content="How does billing work?")], "rewrite_count": 0},
        config={"configurable": {"thread_id": "channel-1"}},
    )

    assert "Billing is monthly." in result["messages"][-1].content


def test_graph_no_context_path_after_rewrite_limit(monkeypatch):
    from agent.graph import build, nodes
    from agent.retrieval import tools

    monkeypatch.setattr(
        nodes,
        "generate_query_or_respond",
        lambda state: {
            "messages": [
                AIMessage(content="", tool_calls=[{"id": "1", "name": "search_outline_docs", "args": {}}])
            ]
        },
    )
    monkeypatch.setattr(tools, "hybrid_search", lambda query, team=None, k=5: [])
    monkeypatch.setattr(nodes, "grade_documents", lambda state: "no_context_found")
    monkeypatch.setattr(
        nodes,
        "no_context_found",
        lambda state: {"messages": [AIMessage(content="Não encontrei isso na documentação.")]},
    )

    graph = build.build_graph(InMemorySaver())
    result = graph.invoke(
        {"messages": [HumanMessage(content="something obscure")], "rewrite_count": 2},
        config={"configurable": {"thread_id": "channel-2"}},
    )

    assert "Não encontrei" in result["messages"][-1].content
