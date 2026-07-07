from datetime import datetime, timedelta, timezone

from agent.db.mongo import sessions_collection

SESSION_TTL = timedelta(hours=1)


def maybe_expire_session(channel_id: str, checkpointer) -> bool:
    session_doc = sessions_collection().find_one({"_id": channel_id})

    is_missing = session_doc is None
    is_stale = (
        session_doc is not None
        and datetime.now(timezone.utc) - session_doc["last_message_at"] > SESSION_TTL
    )

    if is_missing or is_stale:
        checkpointer.delete_thread(channel_id)

    return bool(is_stale)


def touch_session(channel_id: str) -> None:
    sessions_collection().update_one(
        {"_id": channel_id},
        {"$set": {"last_message_at": datetime.now(timezone.utc)}},
        upsert=True,
    )


def reset_session(channel_id: str, checkpointer) -> None:
    checkpointer.delete_thread(channel_id)
    sessions_collection().delete_one({"_id": channel_id})
