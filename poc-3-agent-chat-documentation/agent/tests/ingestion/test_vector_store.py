from unittest.mock import MagicMock

import pytest


@pytest.fixture
def fake_collection():
    return MagicMock()


def test_upsert_document_chunks_deletes_old_then_adds_new(monkeypatch, fake_collection):
    from agent.ingestion import vector_store

    monkeypatch.setattr(vector_store, "chunks_collection", lambda: fake_collection)
    added = []
    monkeypatch.setattr(
        vector_store,
        "get_vector_store",
        lambda: MagicMock(add_documents=lambda docs: added.extend(docs)),
    )

    vector_store.upsert_document_chunks(
        document_id="doc-1",
        chunks=["chunk one", "chunk two"],
        metadata={"source": "https://outline.test/doc/doc-1", "owner": "Billing", "title": "Billing"},
    )

    fake_collection.delete_many.assert_called_once_with({"outline_document_id": "doc-1"})
    assert len(added) == 2
    assert added[0].page_content == "chunk one"
    assert added[0].metadata["outline_document_id"] == "doc-1"
    assert added[0].metadata["chunk_index"] == 0
    assert added[0].metadata["owner"] == "Billing"


def test_delete_document_chunks_removes_by_document_id(fake_collection, monkeypatch):
    from agent.ingestion import vector_store

    monkeypatch.setattr(vector_store, "chunks_collection", lambda: fake_collection)

    vector_store.delete_document_chunks("doc-1")

    fake_collection.delete_many.assert_called_once_with({"outline_document_id": "doc-1"})


def test_get_vector_store_uses_content_as_text_key(monkeypatch, fake_collection):
    """The Atlas Search index and hybrid_retriever._text_leg both expect the chunk
    body to live under the "content" field, so MongoDBAtlasVectorSearch must be
    constructed with text_key="content" (its default is "text")."""
    from agent.ingestion import vector_store

    monkeypatch.setattr(vector_store, "chunks_collection", lambda: fake_collection)

    captured_kwargs = {}

    class FakeMongoDBAtlasVectorSearch:
        def __init__(self, *args, **kwargs):
            captured_kwargs.update(kwargs)

    monkeypatch.setattr(vector_store, "MongoDBAtlasVectorSearch", FakeMongoDBAtlasVectorSearch)
    vector_store.get_vector_store.cache_clear()

    try:
        vector_store.get_vector_store()
    finally:
        vector_store.get_vector_store.cache_clear()

    assert captured_kwargs.get("text_key") == "content"
