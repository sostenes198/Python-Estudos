from types import SimpleNamespace
from unittest.mock import MagicMock


def _chunks():
    return [
        {"content": "Billing runs monthly.", "source": "https://outline.test/doc/1", "owner": "Billing", "title": "Billing"},
        {"content": "Refunds take 5 days.", "source": "https://outline.test/doc/2", "owner": "Billing", "title": "Refunds"},
    ]


def test_generate_grounded_answer_extracts_cited_sources(monkeypatch):
    from agent.citations import anthropic_citations

    fake_citation = SimpleNamespace(document_index=0)
    fake_text_block = SimpleNamespace(type="text", text="Billing runs monthly.", citations=[fake_citation])
    fake_response = SimpleNamespace(content=[fake_text_block])

    fake_client = MagicMock()
    fake_client.messages.create.return_value = fake_response
    monkeypatch.setattr(anthropic_citations, "_get_client", lambda: fake_client)

    answer, sources = anthropic_citations.generate_grounded_answer("How often is billing?", _chunks())

    assert answer == "Billing runs monthly."
    assert sources == [{"source": "https://outline.test/doc/1", "owner": "Billing"}]

    request_content = fake_client.messages.create.call_args.kwargs["messages"][0]["content"]
    assert request_content[0]["type"] == "document"
    assert request_content[0]["citations"] == {"enabled": True}
    assert request_content[-1] == {"type": "text", "text": "How often is billing?"}


def test_generate_grounded_answer_falls_back_to_all_chunks_when_no_citations(monkeypatch):
    from agent.citations import anthropic_citations

    fake_text_block = SimpleNamespace(type="text", text="Some answer.", citations=None)
    fake_response = SimpleNamespace(content=[fake_text_block])

    fake_client = MagicMock()
    fake_client.messages.create.return_value = fake_response
    monkeypatch.setattr(anthropic_citations, "_get_client", lambda: fake_client)

    _, sources = anthropic_citations.generate_grounded_answer("question", _chunks())

    assert sources == [
        {"source": "https://outline.test/doc/1", "owner": "Billing"},
        {"source": "https://outline.test/doc/2", "owner": "Billing"},
    ]
