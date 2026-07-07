def test_rag_state_has_messages_and_rewrite_count():
    from agent.graph.state import RagState

    state: RagState = {"messages": [], "rewrite_count": 0}

    assert state["rewrite_count"] == 0
    assert state["messages"] == []
