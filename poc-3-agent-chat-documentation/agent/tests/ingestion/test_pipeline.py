from unittest.mock import MagicMock


def test_sync_document_fetches_chunks_and_upserts_with_metadata(monkeypatch):
    from agent.ingestion import pipeline

    fake_outline_client = MagicMock()
    fake_outline_client.get_document.return_value = {
        "id": "doc-1",
        "title": "How billing works",
        "text": "# Billing\n\nBilling is monthly.",
        "url": "/doc/how-billing-works-abc123",
        "collectionId": "col-1",
    }
    fake_outline_client.get_owner.return_value = "Billing"
    monkeypatch.setattr(pipeline, "get_outline_client", lambda: fake_outline_client)
    monkeypatch.setattr(pipeline, "chunk_markdown", lambda text: ["chunk a", "chunk b"])

    upsert_calls = []
    monkeypatch.setattr(
        pipeline,
        "upsert_document_chunks",
        lambda document_id, chunks, metadata: upsert_calls.append(
            (document_id, chunks, metadata)
        ),
    )

    pipeline.sync_document("doc-1")

    assert len(upsert_calls) == 1
    document_id, chunks, metadata = upsert_calls[0]
    assert document_id == "doc-1"
    assert chunks == ["chunk a", "chunk b"]
    assert metadata["owner"] == "Billing"
    assert metadata["title"] == "How billing works"
    assert metadata["source"] == "https://outline.example.test/doc/how-billing-works-abc123"


def test_remove_document_deletes_chunks(monkeypatch):
    from agent.ingestion import pipeline

    delete_calls = []
    monkeypatch.setattr(
        pipeline, "delete_document_chunks", lambda document_id: delete_calls.append(document_id)
    )

    pipeline.remove_document("doc-1")

    assert delete_calls == ["doc-1"]
