from functools import lru_cache

from slack_sdk import WebClient
from slack_sdk.signature import SignatureVerifier

from agent.config import get_settings


@lru_cache
def _get_verifier() -> SignatureVerifier:
    return SignatureVerifier(signing_secret=get_settings().slack_signing_secret)


@lru_cache
def _get_client() -> WebClient:
    return WebClient(token=get_settings().slack_bot_token)


def verify_slack_signature(body: bytes, timestamp: str, signature: str) -> bool:
    return _get_verifier().is_valid(body=body, timestamp=timestamp, signature=signature)


def post_message(channel: str, text: str, thread_ts: str | None) -> None:
    kwargs = {"channel": channel, "text": text}
    if thread_ts:
        kwargs["thread_ts"] = thread_ts
    _get_client().chat_postMessage(**kwargs)
