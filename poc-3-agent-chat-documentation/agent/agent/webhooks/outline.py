import hashlib
import hmac
import json

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request

from agent.config import get_settings
from agent.ingestion.pipeline import remove_document, sync_document

router = APIRouter()

_REMOVE_EVENTS = {"documents.delete", "documents.archive"}
_SYNC_EVENTS = {"documents.create", "documents.update", "documents.publish"}


def _verify_signature(body: bytes, signature: str) -> bool:
    secret = get_settings().outline_webhook_secret
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


@router.post("/webhooks/outline")
async def receive_outline_webhook(request: Request, background_tasks: BackgroundTasks):
    body = await request.body()
    signature = request.headers.get("Outline-Signature", "")

    if not _verify_signature(body, signature):
        raise HTTPException(status_code=401, detail="invalid signature")

    event = json.loads(body)
    event_name = event["event"]
    document_id = event["payload"]["model"]["id"]

    if event_name in _SYNC_EVENTS:
        background_tasks.add_task(sync_document, document_id)
    elif event_name in _REMOVE_EVENTS:
        background_tasks.add_task(remove_document, document_id)

    return {"status": "accepted"}
