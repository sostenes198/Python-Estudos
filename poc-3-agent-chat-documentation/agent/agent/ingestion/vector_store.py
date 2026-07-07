from functools import lru_cache

from langchain_core.documents import Document
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings

from agent.db.mongo import chunks_collection


@lru_cache
def get_vector_store() -> MongoDBAtlasVectorSearch:
    return MongoDBAtlasVectorSearch(
        embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
        collection=chunks_collection(),
        index_name="vector_index",
        relevance_score_fn="cosine",
    )


def upsert_document_chunks(document_id: str, chunks: list[str], metadata: dict) -> None:
    chunks_collection().delete_many({"outline_document_id": document_id})

    documents = [
        Document(
            page_content=chunk,
            metadata={
                **metadata,
                "outline_document_id": document_id,
                "chunk_index": index,
            },
        )
        for index, chunk in enumerate(chunks)
    ]
    get_vector_store().add_documents(documents)


def delete_document_chunks(document_id: str) -> None:
    chunks_collection().delete_many({"outline_document_id": document_id})
