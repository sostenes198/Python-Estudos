from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock


def test_maybe_expire_session_returns_false_for_brand_new_channel(monkeypatch):
    from agent.chat import session

    fake_collection = MagicMock()
    fake_collection.find_one.return_value = None
    monkeypatch.setattr(session, "sessions_collection", lambda: fake_collection)

    fake_checkpointer = MagicMock()

    expired = session.maybe_expire_session("channel-1", fake_checkpointer)

    assert expired is False
    fake_checkpointer.delete_thread.assert_called_once_with("channel-1")


def test_maybe_expire_session_returns_true_and_resets_when_stale(monkeypatch):
    from agent.chat import session

    stale_time = datetime.now(timezone.utc) - timedelta(hours=2)
    fake_collection = MagicMock()
    fake_collection.find_one.return_value = {"_id": "channel-1", "last_message_at": stale_time}
    monkeypatch.setattr(session, "sessions_collection", lambda: fake_collection)

    fake_checkpointer = MagicMock()

    expired = session.maybe_expire_session("channel-1", fake_checkpointer)

    assert expired is True
    fake_checkpointer.delete_thread.assert_called_once_with("channel-1")


def test_maybe_expire_session_returns_false_when_recent(monkeypatch):
    from agent.chat import session

    recent_time = datetime.now(timezone.utc) - timedelta(minutes=5)
    fake_collection = MagicMock()
    fake_collection.find_one.return_value = {"_id": "channel-1", "last_message_at": recent_time}
    monkeypatch.setattr(session, "sessions_collection", lambda: fake_collection)

    fake_checkpointer = MagicMock()

    expired = session.maybe_expire_session("channel-1", fake_checkpointer)

    assert expired is False
    fake_checkpointer.delete_thread.assert_not_called()


def test_touch_session_upserts_last_message_at(monkeypatch):
    from agent.chat import session

    fake_collection = MagicMock()
    monkeypatch.setattr(session, "sessions_collection", lambda: fake_collection)

    session.touch_session("channel-1")

    args, kwargs = fake_collection.update_one.call_args
    assert args[0] == {"_id": "channel-1"}
    assert "last_message_at" in args[1]["$set"]
    assert kwargs["upsert"] is True


def test_reset_session_deletes_thread_and_session_doc(monkeypatch):
    from agent.chat import session

    fake_collection = MagicMock()
    monkeypatch.setattr(session, "sessions_collection", lambda: fake_collection)
    fake_checkpointer = MagicMock()

    session.reset_session("channel-1", fake_checkpointer)

    fake_checkpointer.delete_thread.assert_called_once_with("channel-1")
    fake_collection.delete_one.assert_called_once_with({"_id": "channel-1"})
