def test_get_db_uses_default_database_from_uri():
    from agent.db.mongo import get_db, get_mongo_client

    get_mongo_client.cache_clear()

    db = get_db()

    assert db.name == "outline_rag_test"
