import time
from unittest.mock import MagicMock

from slack_sdk.signature import SignatureVerifier


def test_verify_slack_signature_accepts_correctly_signed_request():
    from agent.chat import slack_client

    verifier = SignatureVerifier(signing_secret="slack_test")
    timestamp = str(int(time.time()))
    body = b"payload=hello"
    signature = verifier.generate_signature(timestamp=timestamp, body=body)

    assert slack_client.verify_slack_signature(body, timestamp, signature) is True


def test_verify_slack_signature_rejects_tampered_body():
    from agent.chat import slack_client

    verifier = SignatureVerifier(signing_secret="slack_test")
    timestamp = str(int(time.time()))
    signature = verifier.generate_signature(timestamp=timestamp, body=b"payload=hello")

    assert slack_client.verify_slack_signature(b"payload=tampered", timestamp, signature) is False


def test_post_message_calls_chat_post_message_with_thread_ts(monkeypatch):
    from agent.chat import slack_client

    fake_client = MagicMock()
    monkeypatch.setattr(slack_client, "_get_client", lambda: fake_client)

    slack_client.post_message(channel="D123", text="hello", thread_ts="169999.0001")

    fake_client.chat_postMessage.assert_called_once_with(
        channel="D123", text="hello", thread_ts="169999.0001"
    )


def test_post_message_omits_thread_ts_when_none(monkeypatch):
    from agent.chat import slack_client

    fake_client = MagicMock()
    monkeypatch.setattr(slack_client, "_get_client", lambda: fake_client)

    slack_client.post_message(channel="D123", text="hello", thread_ts=None)

    fake_client.chat_postMessage.assert_called_once_with(channel="D123", text="hello")
