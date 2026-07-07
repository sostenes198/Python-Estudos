from agent.config import get_settings
from agent.ingestion.chunker import chunk_markdown
from agent.ingestion.outline_client import get_outline_client
from agent.ingestion.vector_store import delete_document_chunks, upsert_document_chunks


def sync_document(document_id: str) -> None:
    outline_client = get_outline_client()
    document = outline_client.get_document(document_id)
    owner = outline_client.get_owner(document["collectionId"])

    chunks = chunk_markdown(document["text"])
    metadata = {
        "source": f"{get_settings().outline_base_url}{document['url']}",
        "title": document["title"],
        "owner": owner,
        "collection_id": document["collectionId"],
    }
    upsert_document_chunks(document_id=document_id, chunks=chunks, metadata=metadata)


def remove_document(document_id: str) -> None:
    delete_document_chunks(document_id)
