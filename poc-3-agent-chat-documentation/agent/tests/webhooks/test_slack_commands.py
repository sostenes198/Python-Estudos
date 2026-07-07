import time
from unittest.mock import MagicMock
from urllib.parse import urlencode

from fastapi import FastAPI
from fastapi.testclient import TestClient
from slack_sdk.signature import SignatureVerifier


def make_app():
    from agent.webhooks.slack_commands import router

    app = FastAPI()
    app.include_router(router)
    return app


def sign(body: bytes):
    verifier = SignatureVerifier(signing_secret="slack_test")
    timestamp = str(int(time.time()))
    signature = verifier.generate_signature(timestamp=timestamp, body=body)
    return timestamp, signature


def test_nova_conversa_resets_session_and_replies_ephemeral(monkeypatch):
    from agent.webhooks import slack_commands

    reset_calls = []
    monkeypatch.setattr(
        slack_commands, "reset_session", lambda channel_id, checkpointer: reset_calls.append(channel_id)
    )
    monkeypatch.setattr(slack_commands, "get_checkpointer", lambda: MagicMock())

    body = urlencode({"command": "/nova-conversa", "channel_id": "D123", "user_id": "U1"}).encode()
    timestamp, signature = sign(body)

    client = TestClient(make_app())
    response = client.post(
        "/webhooks/slack/commands",
        content=body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Slack-Request-Timestamp": timestamp,
            "X-Slack-Signature": signature,
        },
    )

    assert response.status_code == 200
    assert response.json()["response_type"] == "ephemeral"
    assert reset_calls == ["D123"]


def test_invalid_signature_rejected():
    body = urlencode({"command": "/nova-conversa", "channel_id": "D123", "user_id": "U1"}).encode()

    client = TestClient(make_app())
    response = client.post(
        "/webhooks/slack/commands",
        content=body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Slack-Request-Timestamp": "1",
            "X-Slack-Signature": "bad",
        },
    )

    assert response.status_code == 401
