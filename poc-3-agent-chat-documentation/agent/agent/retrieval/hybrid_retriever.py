from agent.db.mongo import chunks_collection
from agent.ingestion.vector_store import get_vector_store

_RRF_K = 60


def _chunk_key(document_id: str, chunk_index: int) -> tuple[str, int]:
    return (document_id, chunk_index)


def _vector_leg(query: str, over_fetch: int) -> list[dict]:
    results = get_vector_store().similarity_search_with_score(query, k=over_fetch)
    ranked = []
    for rank, (doc, _score) in enumerate(results, start=1):
        ranked.append(
            {
                "key": _chunk_key(doc.metadata["outline_document_id"], doc.metadata["chunk_index"]),
                "rank": rank,
                "content": doc.page_content,
                "source": doc.metadata["source"],
                "owner": doc.metadata["owner"],
                "title": doc.metadata["title"],
            }
        )
    return ranked


def _text_leg(query: str, over_fetch: int) -> list[dict]:
    pipeline = [
        {
            "$search": {
                "index": "text_index",
                "text": {"query": query, "path": "content"},
            }
        },
        {"$limit": over_fetch},
    ]
    ranked = []
    for rank, hit in enumerate(chunks_collection().aggregate(pipeline), start=1):
        ranked.append(
            {
                "key": _chunk_key(hit["outline_document_id"], hit["chunk_index"]),
                "rank": rank,
                "content": hit["content"],
                "source": hit["source"],
                "owner": hit["owner"],
                "title": hit["title"],
            }
        )
    return ranked


def hybrid_search(query: str, team: str | None = None, k: int = 5) -> list[dict]:
    over_fetch = max(k * 3, 15)
    vector_hits = _vector_leg(query, over_fetch)
    text_hits = _text_leg(query, over_fetch)

    fused: dict[tuple[str, int], dict] = {}
    scores: dict[tuple[str, int], float] = {}

    for leg in (vector_hits, text_hits):
        for hit in leg:
            key = hit["key"]
            fused.setdefault(key, hit)
            scores[key] = scores.get(key, 0.0) + 1.0 / (_RRF_K + hit["rank"])

    candidates = list(fused.values())
    if team:
        candidates = [c for c in candidates if c["owner"] == team]

    candidates.sort(key=lambda c: scores[c["key"]], reverse=True)

    return [
        {"content": c["content"], "source": c["source"], "owner": c["owner"], "title": c["title"]}
        for c in candidates[:k]
    ]
