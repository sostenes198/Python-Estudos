import json
from unittest.mock import MagicMock

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage


def _tool_message(chunks):
    return ToolMessage(content=json.dumps(chunks), tool_call_id="1", name="search_outline_docs")


def test_grade_documents_routes_to_generate_answer_when_relevant(monkeypatch):
    from agent.graph import nodes

    fake_grader = MagicMock()
    fake_grader.with_structured_output.return_value.invoke.return_value = MagicMock(binary_score="yes")
    monkeypatch.setattr(nodes, "_grader_model", fake_grader)

    state = {
        "messages": [
            HumanMessage(content="How does billing work?"),
            AIMessage(content="", tool_calls=[{"id": "1", "name": "search_outline_docs", "args": {}}]),
            _tool_message([{"content": "Billing is monthly.", "source": "s", "owner": "Billing", "title": "t"}]),
        ],
        "rewrite_count": 0,
    }

    assert nodes.grade_documents(state) == "generate_answer"


def test_grade_documents_routes_to_rewrite_when_not_relevant_and_under_limit(monkeypatch):
    from agent.graph import nodes

    fake_grader = MagicMock()
    fake_grader.with_structured_output.return_value.invoke.return_value = MagicMock(binary_score="no")
    monkeypatch.setattr(nodes, "_grader_model", fake_grader)

    state = {
        "messages": [
            HumanMessage(content="How does billing work?"),
            AIMessage(content="", tool_calls=[{"id": "1", "name": "search_outline_docs", "args": {}}]),
            _tool_message([]),
        ],
        "rewrite_count": 0,
    }

    assert nodes.grade_documents(state) == "rewrite_question"


def test_grade_documents_routes_to_no_context_found_after_two_rewrites(monkeypatch):
    from agent.graph import nodes

    fake_grader = MagicMock()
    fake_grader.with_structured_output.return_value.invoke.return_value = MagicMock(binary_score="no")
    monkeypatch.setattr(nodes, "_grader_model", fake_grader)

    state = {
        "messages": [
            HumanMessage(content="How does billing work?"),
            AIMessage(content="", tool_calls=[{"id": "1", "name": "search_outline_docs", "args": {}}]),
            _tool_message([]),
        ],
        "rewrite_count": 2,
    }

    assert nodes.grade_documents(state) == "no_context_found"


def test_rewrite_question_increments_rewrite_count(monkeypatch):
    from agent.graph import nodes

    fake_model = MagicMock()
    fake_model.invoke.return_value = AIMessage(content="What is the billing cadence?")
    monkeypatch.setattr(nodes, "_response_model", fake_model)

    state = {"messages": [HumanMessage(content="billing?")], "rewrite_count": 0}

    result = nodes.rewrite_question(state)

    assert result["rewrite_count"] == 1
    assert result["messages"][0].content == "What is the billing cadence?"


def test_generate_answer_uses_citations_helper_and_appends_sources(monkeypatch):
    from agent.graph import nodes

    chunks = [{"content": "Billing is monthly.", "source": "https://x/1", "owner": "Billing", "title": "t"}]
    monkeypatch.setattr(
        nodes,
        "generate_grounded_answer",
        lambda question, chunks: ("Billing is monthly.", [{"source": "https://x/1", "owner": "Billing"}]),
    )

    state = {
        "messages": [HumanMessage(content="How does billing work?"), _tool_message(chunks)],
        "rewrite_count": 0,
    }

    result = nodes.generate_answer(state)

    answer_message = result["messages"][0]
    assert "Billing is monthly." in answer_message.content
    assert "https://x/1" in answer_message.content


def test_no_context_found_returns_fixed_message():
    from agent.graph import nodes

    state = {"messages": [HumanMessage(content="anything")], "rewrite_count": 2}

    result = nodes.no_context_found(state)

    assert "não encontrei" in result["messages"][0].content.lower()
