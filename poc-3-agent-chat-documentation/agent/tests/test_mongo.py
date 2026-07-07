def test_get_db_uses_default_database_from_uri():
    from agent.db.mongo import get_db, get_mongo_client

    get_mongo_client.cache_clear()

    db = get_db()

    assert db.name == "outline_rag_test"


def test_datetimes_read_back_from_real_mongo_are_tz_aware():
    """Regression test for Task 15 review finding: MongoClient must be constructed
    with tz_aware=True, otherwise datetimes read back from a real collection are
    naive and session.py's `datetime.now(timezone.utc) - session_doc["last_message_at"]`
    raises TypeError on the very first real session lookup.
    """
    from agent.chat.session import touch_session
    from agent.db.mongo import get_mongo_client, sessions_collection

    get_mongo_client.cache_clear()

    channel_id = "test-tz-aware-regression-channel"
    collection = sessions_collection()

    try:
        touch_session(channel_id)

        doc = collection.find_one({"_id": channel_id})

        assert doc is not None
        assert doc["last_message_at"].tzinfo is not None
    finally:
        collection.delete_one({"_id": channel_id})
