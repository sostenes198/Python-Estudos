import json


def test_search_outline_docs_returns_json_encoded_hits(monkeypatch):
    from agent.retrieval import tools

    monkeypatch.setattr(
        tools,
        "hybrid_search",
        lambda query, team=None, k=5: [
            {"content": "billing is monthly", "source": "https://outline.test/doc/1", "owner": "Billing", "title": "Billing"}
        ],
    )

    result = tools.search_outline_docs.invoke({"query": "how does billing work"})

    parsed = json.loads(result)
    assert parsed == [
        {"content": "billing is monthly", "source": "https://outline.test/doc/1", "owner": "Billing", "title": "Billing"}
    ]
