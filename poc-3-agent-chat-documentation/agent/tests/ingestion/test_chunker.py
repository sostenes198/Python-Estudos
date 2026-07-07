def test_chunk_markdown_splits_on_headers_and_respects_size():
    from agent.ingestion.chunker import chunk_markdown

    text = (
        "# Billing overview\n\n"
        + ("Billing details. " * 80)
        + "\n\n## Refunds\n\n"
        + ("Refund details. " * 80)
    )

    chunks = chunk_markdown(text)

    assert len(chunks) >= 2
    assert all(len(c) <= 1200 for c in chunks)
    assert any("Refunds" in c or "Refund details" in c for c in chunks)
