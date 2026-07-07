from unittest.mock import MagicMock

from langchain_core.documents import Document


def _doc(content, document_id, chunk_index, owner="Billing"):
    return Document(
        page_content=content,
        metadata={
            "outline_document_id": document_id,
            "chunk_index": chunk_index,
            "source": f"https://outline.test/doc/{document_id}",
            "owner": owner,
            "title": document_id,
        },
    )


def test_hybrid_search_merges_vector_and_text_results_by_rrf(monkeypatch):
    from agent.retrieval import hybrid_retriever

    vector_results = [
        (_doc("vector hit one", "doc-1", 0), 0.95),
        (_doc("vector hit two", "doc-2", 0), 0.80),
    ]
    fake_vector_store = MagicMock()
    fake_vector_store.similarity_search_with_score.return_value = vector_results
    monkeypatch.setattr(hybrid_retriever, "get_vector_store", lambda: fake_vector_store)

    text_hits = [
        {
            "outline_document_id": "doc-2",
            "chunk_index": 0,
            "content": "vector hit two",
            "source": "https://outline.test/doc/doc-2",
            "owner": "Billing",
            "title": "doc-2",
        },
        {
            "outline_document_id": "doc-3",
            "chunk_index": 0,
            "content": "text-only hit",
            "source": "https://outline.test/doc/doc-3",
            "owner": "Pay",
            "title": "doc-3",
        },
    ]
    fake_collection = MagicMock()
    fake_collection.aggregate.return_value = text_hits
    monkeypatch.setattr(hybrid_retriever, "chunks_collection", lambda: fake_collection)

    results = hybrid_retriever.hybrid_search("how does billing work", k=5)

    ids = [(r["content"]) for r in results]
    assert "vector hit two" in ids  # appears in both legs, should rank highly
    assert len(results) == 3  # doc-1, doc-2, doc-3 deduped


def test_hybrid_search_filters_by_team(monkeypatch):
    from agent.retrieval import hybrid_retriever

    fake_vector_store = MagicMock()
    fake_vector_store.similarity_search_with_score.return_value = [
        (_doc("billing content", "doc-1", 0, owner="Billing"), 0.9),
        (_doc("pay content", "doc-2", 0, owner="Pay"), 0.9),
    ]
    monkeypatch.setattr(hybrid_retriever, "get_vector_store", lambda: fake_vector_store)

    fake_collection = MagicMock()
    fake_collection.aggregate.return_value = []
    monkeypatch.setattr(hybrid_retriever, "chunks_collection", lambda: fake_collection)

    results = hybrid_retriever.hybrid_search("question", team="Pay", k=5)

    assert len(results) == 1
    assert results[0]["owner"] == "Pay"
