import json
import time
from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient
from slack_sdk.signature import SignatureVerifier


def make_app():
    from agent.webhooks.slack_events import router

    app = FastAPI()
    app.include_router(router)
    return app


def sign(body: bytes):
    verifier = SignatureVerifier(signing_secret="slack_test")
    timestamp = str(int(time.time()))
    signature = verifier.generate_signature(timestamp=timestamp, body=body)
    return timestamp, signature


def test_url_verification_challenge_is_echoed_back():
    body = json.dumps({"type": "url_verification", "challenge": "abc123"}).encode()
    timestamp, signature = sign(body)

    client = TestClient(make_app())
    response = client.post(
        "/webhooks/slack/events",
        content=body,
        headers={"X-Slack-Request-Timestamp": timestamp, "X-Slack-Signature": signature},
    )

    assert response.status_code == 200
    assert response.json() == {"challenge": "abc123"}


def test_dm_message_is_enqueued_for_background_processing(monkeypatch):
    from agent.webhooks import slack_events

    calls = []
    monkeypatch.setattr(slack_events, "handle_message_event", lambda event: calls.append(event))

    body = json.dumps(
        {
            "type": "event_callback",
            "event": {
                "type": "message",
                "channel": "D123",
                "channel_type": "im",
                "user": "U1",
                "text": "oi",
                "ts": "169999.0001",
            },
        }
    ).encode()
    timestamp, signature = sign(body)

    client = TestClient(make_app())
    response = client.post(
        "/webhooks/slack/events",
        content=body,
        headers={"X-Slack-Request-Timestamp": timestamp, "X-Slack-Signature": signature},
    )

    assert response.status_code == 200
    assert len(calls) == 1
    assert calls[0]["channel"] == "D123"


def test_bot_messages_are_ignored(monkeypatch):
    from agent.webhooks import slack_events

    calls = []
    monkeypatch.setattr(slack_events, "handle_message_event", lambda event: calls.append(event))

    body = json.dumps(
        {
            "type": "event_callback",
            "event": {
                "type": "message",
                "channel": "D123",
                "channel_type": "im",
                "bot_id": "B1",
                "text": "resposta do proprio bot",
                "ts": "169999.0002",
            },
        }
    ).encode()
    timestamp, signature = sign(body)

    client = TestClient(make_app())
    client.post(
        "/webhooks/slack/events",
        content=body,
        headers={"X-Slack-Request-Timestamp": timestamp, "X-Slack-Signature": signature},
    )

    assert calls == []


def test_invalid_signature_rejected():
    body = json.dumps({"type": "url_verification", "challenge": "abc123"}).encode()

    client = TestClient(make_app())
    response = client.post(
        "/webhooks/slack/events",
        content=body,
        headers={"X-Slack-Request-Timestamp": "1", "X-Slack-Signature": "bad"},
    )

    assert response.status_code == 401


def test_handle_message_event_runs_graph_and_replies(monkeypatch):
    from agent.webhooks import slack_events

    monkeypatch.setattr(slack_events, "maybe_expire_session", lambda channel_id, checkpointer: False)
    touched = []
    monkeypatch.setattr(slack_events, "touch_session", lambda channel_id: touched.append(channel_id))

    fake_graph = MagicMock()
    fake_graph.invoke.return_value = {"messages": [MagicMock(content="Billing is monthly.\n\nFontes:\n- Billing: s")]}
    monkeypatch.setattr(slack_events, "build_graph", lambda checkpointer: fake_graph)
    monkeypatch.setattr(slack_events, "get_checkpointer", lambda: MagicMock())

    posted = []
    monkeypatch.setattr(slack_events, "post_message", lambda channel, text, thread_ts: posted.append((channel, text, thread_ts)))

    logged = []
    fake_log_collection = MagicMock()
    fake_log_collection.insert_many.side_effect = lambda docs: logged.extend(docs)
    monkeypatch.setattr(slack_events, "conversation_log_collection", lambda: fake_log_collection)

    slack_events.handle_message_event(
        {"channel": "D123", "user": "U1", "text": "how does billing work?", "ts": "169999.0001"}
    )

    assert touched == ["D123"]
    assert posted[0][0] == "D123"
    assert "Billing is monthly." in posted[0][1]
    assert posted[0][2] is None
    assert len(logged) == 2
    assert logged[0]["role"] == "user"
    assert logged[1]["role"] == "assistant"
