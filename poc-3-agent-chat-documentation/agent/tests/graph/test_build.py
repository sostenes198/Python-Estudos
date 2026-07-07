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
        {
            "messages": [HumanMessage(content="How does billing work?")],
            "rewrite_count": 0,
            "current_question": "How does billing work?",
        },
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
        {
            "messages": [HumanMessage(content="something obscure")],
            "rewrite_count": 2,
            "current_question": "something obscure",
        },
        config={"configurable": {"thread_id": "channel-2"}},
    )

    assert "Não encontrei" in result["messages"][-1].content


def test_multi_turn_conversation_answers_current_question_not_stale_first_message(monkeypatch):
    """Regression test: with a persisted checkpointer and a shared thread_id (simulating two
    sequential Slack DM messages in the same channel), the second turn must be graded/answered
    against ITS OWN question, not the first message of the whole conversation. Before the fix,
    nodes read `state["messages"][0].content`, which `add_messages` never overwrites, so turn 2
    would be answered as if it were still asking about turn 1's topic.
    """
    from agent.graph import build, nodes
    from agent.retrieval import tools

    def fake_generate_query_or_respond(state):
        last_message = state["messages"][-1]
        if isinstance(last_message, HumanMessage):
            return {
                "messages": [
                    AIMessage(
                        content="",
                        tool_calls=[
                            {
                                "id": "1",
                                "name": "search_outline_docs",
                                "args": {"query": state["current_question"]},
                            }
                        ],
                    )
                ]
            }
        return {"messages": [AIMessage(content="should not reach here")]}

    monkeypatch.setattr(nodes, "generate_query_or_respond", fake_generate_query_or_respond)
    monkeypatch.setattr(
        tools,
        "hybrid_search",
        lambda query, team=None, k=5: [
            {"content": "some indexed content", "source": "s", "owner": "Docs", "title": "t"}
        ],
    )
    monkeypatch.setattr(nodes, "grade_documents", lambda state: "generate_answer")
    # generate_answer itself is NOT mocked: we want the real node, which must read
    # state["current_question"] (post-fix) rather than state["messages"][0].content (pre-fix).
    monkeypatch.setattr(
        nodes,
        "generate_grounded_answer",
        lambda question, chunks: (f"Answer about: {question}", []),
    )

    checkpointer = InMemorySaver()
    graph = build.build_graph(checkpointer)
    thread_id = "channel-multi-turn"
    config = {"configurable": {"thread_id": thread_id}}
    # Locks the channel_id-not-thread_ts invariant: the graph is keyed on a single, stable
    # thread_id per channel, exactly this shape.
    assert config == {"configurable": {"thread_id": "channel-multi-turn"}}

    result_1 = graph.invoke(
        {
            "messages": [HumanMessage(content="how does billing work?")],
            "rewrite_count": 0,
            "current_question": "how does billing work?",
        },
        config=config,
    )
    assert result_1["messages"][-1].content == "Answer about: how does billing work?"

    result_2 = graph.invoke(
        {
            "messages": [HumanMessage(content="what about refunds?")],
            "rewrite_count": 0,
            "current_question": "what about refunds?",
        },
        config=config,
    )

    assert result_2["messages"][-1].content == "Answer about: what about refunds?"
    assert "billing" not in result_2["messages"][-1].content.lower()
