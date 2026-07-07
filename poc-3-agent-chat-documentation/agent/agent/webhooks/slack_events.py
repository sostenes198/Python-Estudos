import json
from functools import lru_cache

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.mongodb import MongoDBSaver

from agent.chat.session import maybe_expire_session, touch_session
from agent.chat.slack_client import post_message, verify_slack_signature
from agent.config import get_settings
from agent.db.mongo import conversation_log_collection
from agent.graph.build import build_graph

router = APIRouter()


@lru_cache
def get_checkpointer() -> MongoDBSaver:
    return MongoDBSaver.from_conn_string(get_settings().mongodb_uri)


def handle_message_event(event: dict) -> None:
    channel_id = event["channel"]
    text = event["text"]

    checkpointer = get_checkpointer()
    expired = maybe_expire_session(channel_id, checkpointer)
    touch_session(channel_id)

    conversation_log_collection().insert_many(
        [{"channel_id": channel_id, "role": "user", "text": text, "sources": [], "created_at": event["ts"]}]
    )

    graph = build_graph(checkpointer)
    result = graph.invoke(
        {"messages": [HumanMessage(content=text)], "rewrite_count": 0},
        config={"configurable": {"thread_id": channel_id}},
    )
    answer = result["messages"][-1].content

    if expired:
        answer = "Nossa conversa anterior expirou por inatividade — começando um papo novo!\n\n" + answer

    conversation_log_collection().insert_many(
        [{"channel_id": channel_id, "role": "assistant", "text": answer, "sources": [], "created_at": None}]
    )

    post_message(channel=channel_id, text=answer, thread_ts=None)


@router.post("/webhooks/slack/events")
async def receive_slack_event(request: Request, background_tasks: BackgroundTasks):
    body = await request.body()
    timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
    signature = request.headers.get("X-Slack-Signature", "")

    if not verify_slack_signature(body, timestamp, signature):
        raise HTTPException(status_code=401, detail="invalid signature")

    payload = json.loads(body)

    if payload.get("type") == "url_verification":
        return {"challenge": payload["challenge"]}

    event = payload.get("event", {})
    if (
        event.get("type") == "message"
        and event.get("channel_type") == "im"
        and "bot_id" not in event
    ):
        background_tasks.add_task(handle_message_event, event)

    return {"status": "accepted"}
