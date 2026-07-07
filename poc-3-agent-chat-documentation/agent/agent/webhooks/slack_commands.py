from urllib.parse import parse_qs

from fastapi import APIRouter, HTTPException, Request

from agent.chat.session import reset_session
from agent.chat.slack_client import verify_slack_signature
from agent.webhooks.slack_events import get_checkpointer

router = APIRouter()


@router.post("/webhooks/slack/commands")
async def receive_slack_command(request: Request):
    body = await request.body()
    timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
    signature = request.headers.get("X-Slack-Signature", "")

    if not verify_slack_signature(body, timestamp, signature):
        raise HTTPException(status_code=401, detail="invalid signature")

    form = {k: v[0] for k, v in parse_qs(body.decode()).items()}

    if form.get("command") == "/nova-conversa":
        reset_session(form["channel_id"], get_checkpointer())
        return {"response_type": "ephemeral", "text": "Conversa encerrada! Pode me chamar quando quiser 👋"}

    return {"response_type": "ephemeral", "text": "Comando não reconhecido."}
