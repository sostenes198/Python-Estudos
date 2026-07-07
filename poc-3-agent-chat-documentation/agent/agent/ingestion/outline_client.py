from functools import lru_cache

import httpx


class OutlineClient:
    def __init__(self, base_url: str, api_token: str):
        self._http = httpx.Client(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_token}"},
            timeout=20.0,
        )
        self._collection_name_cache: dict[str, str] = {}

    def get_document(self, document_id: str) -> dict:
        response = self._http.post("/api/documents.info", json={"id": document_id})
        response.raise_for_status()
        return response.json()["data"]

    def get_collection(self, collection_id: str) -> dict:
        response = self._http.post("/api/collections.info", json={"id": collection_id})
        response.raise_for_status()
        return response.json()["data"]

    def get_owner(self, collection_id: str) -> str:
        if collection_id not in self._collection_name_cache:
            collection = self.get_collection(collection_id)
            self._collection_name_cache[collection_id] = collection["name"]
        return self._collection_name_cache[collection_id]


@lru_cache
def get_outline_client() -> OutlineClient:
    from agent.config import get_settings

    settings = get_settings()
    return OutlineClient(
        base_url=settings.outline_base_url, api_token=settings.outline_api_token
    )
