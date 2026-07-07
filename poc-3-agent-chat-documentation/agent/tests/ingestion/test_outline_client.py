import httpx
import pytest


class FakeTransport(httpx.BaseTransport):
    def __init__(self, responses: dict[str, dict]):
        self.responses = responses
        self.requests: list[httpx.Request] = []

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        body = self.responses[request.url.path]
        return httpx.Response(200, json=body, request=request)


def make_client(responses):
    from agent.ingestion.outline_client import OutlineClient

    transport = FakeTransport(responses)
    client = OutlineClient(base_url="https://outline.test", api_token="ol_test")
    http_client = httpx.Client(
        base_url="https://outline.test",
        headers={"Authorization": "Bearer ol_test"},
        transport=transport,
    )
    client._http = http_client
    client._http.transport = transport  # Store transport reference for testing
    return client


def test_get_document_posts_id_and_returns_data():
    client = make_client(
        {
            "/api/documents.info": {
                "data": {
                    "id": "doc-1",
                    "title": "How billing works",
                    "text": "# Billing\n\nBilling is monthly.",
                    "url": "/doc/how-billing-works-abc123",
                    "collectionId": "col-1",
                }
            }
        }
    )

    document = client.get_document("doc-1")

    assert document["id"] == "doc-1"
    assert document["collectionId"] == "col-1"
    assert client._http.transport.requests[0].url.path == "/api/documents.info"


def test_get_owner_returns_collection_name_and_caches(monkeypatch):
    client = make_client(
        {"/api/collections.info": {"data": {"id": "col-1", "name": "Billing"}}}
    )

    owner_first_call = client.get_owner("col-1")
    owner_second_call = client.get_owner("col-1")

    assert owner_first_call == "Billing"
    assert owner_second_call == "Billing"
    assert len(client._http.transport.requests) == 1
