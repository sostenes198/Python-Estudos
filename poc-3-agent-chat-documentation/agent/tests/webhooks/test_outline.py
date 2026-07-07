import hashlib
import hmac
import json
import time

from fastapi import FastAPI
from fastapi.testclient import TestClient


def make_app():
    from agent.webhooks.outline import router

    app = FastAPI()
    app.include_router(router)
    return app


def sign(body: bytes, secret: str) -> str:
    timestamp = str(int(time.time() * 1000))
    payload = f"{timestamp}.{body.decode()}".encode()
    signature = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return f"t={timestamp},s={signature}"


def test_valid_signature_enqueues_sync_for_update_event(monkeypatch):
    from agent.webhooks import outline

    calls = []
    monkeypatch.setattr(outline, "sync_document", lambda document_id: calls.append(("sync", document_id)))
    monkeypatch.setattr(outline, "remove_document", lambda document_id: calls.append(("remove", document_id)))

    client = TestClient(make_app())
    payload = {"event": "documents.update", "payload": {"model": {"id": "doc-1"}}}
    body = json.dumps(payload).encode()

    response = client.post(
        "/webhooks/outline",
        content=body,
        headers={"Outline-Signature": sign(body, "whsec_test")},
    )

    assert response.status_code == 200
    assert calls == [("sync", "doc-1")]


def test_delete_event_enqueues_remove(monkeypatch):
    from agent.webhooks import outline

    calls = []
    monkeypatch.setattr(outline, "sync_document", lambda document_id: calls.append(("sync", document_id)))
    monkeypatch.setattr(outline, "remove_document", lambda document_id: calls.append(("remove", document_id)))

    client = TestClient(make_app())
    payload = {"event": "documents.delete", "payload": {"model": {"id": "doc-1"}}}
    body = json.dumps(payload).encode()

    response = client.post(
        "/webhooks/outline",
        content=body,
        headers={"Outline-Signature": sign(body, "whsec_test")},
    )

    assert response.status_code == 200
    assert calls == [("remove", "doc-1")]


def test_invalid_signature_is_rejected(monkeypatch):
    from agent.webhooks import outline

    calls = []
    monkeypatch.setattr(outline, "sync_document", lambda document_id: calls.append(document_id))

    client = TestClient(make_app())
    body = json.dumps({"event": "documents.update", "payload": {"model": {"id": "doc-1"}}}).encode()

    response = client.post(
        "/webhooks/outline",
        content=body,
        headers={"Outline-Signature": "t=1234567890,s=deadbeef"},
    )

    assert response.status_code == 401
    assert calls == []


def test_malformed_signature_header_is_rejected(monkeypatch):
    from agent.webhooks import outline

    calls = []
    monkeypatch.setattr(outline, "sync_document", lambda document_id: calls.append(document_id))

    client = TestClient(make_app())
    body = json.dumps({"event": "documents.update", "payload": {"model": {"id": "doc-1"}}}).encode()

    response = client.post(
        "/webhooks/outline",
        content=body,
        headers={"Outline-Signature": "deadbeef"},
    )

    assert response.status_code == 401
    assert calls == []
