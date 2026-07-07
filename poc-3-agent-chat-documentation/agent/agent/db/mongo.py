from functools import lru_cache

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from agent.config import get_settings


@lru_cache
def get_mongo_client() -> MongoClient:
    return MongoClient(get_settings().mongodb_uri)


def get_db() -> Database:
    return get_mongo_client().get_default_database()


def chunks_collection() -> Collection:
    return get_db()["outline_chunks"]


def sessions_collection() -> Collection:
    return get_db()["conversation_sessions"]


def conversation_log_collection() -> Collection:
    return get_db()["conversation_log"]
