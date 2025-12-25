from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from pymongo import MongoClient
from pymongo.database import Database

from server.core.config import Settings, load_settings
from server.core.logger import get_logger

log = get_logger("optiresume.db")


def _mask_mongo_uri(uri: str) -> str:
    if not uri:
        return ""
    if "@" in uri:
        _, right = uri.split("@", 1)
        return "***@" + right
    return uri


@dataclass
class Mongo:
    client: MongoClient
    db: Database


_mongo: Optional[Mongo] = None


def connect(settings: Optional[Settings] = None) -> Mongo:
    global _mongo
    if _mongo:
        return _mongo

    s = settings or load_settings()
    if not s.mongo_uri:
        raise RuntimeError("Missing MONGO_URI (or MONGODB_URI) in environment")
    if not s.mongo_db_name:
        raise RuntimeError("Missing MONGO_DB_NAME (or DB_NAME) in environment")

    client = MongoClient(
        s.mongo_uri,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
    )

    try:
        client.admin.command("ping")
    except Exception:
        log.exception(
            "MongoDB ping failed",
            extra={
                "mongo_uri": _mask_mongo_uri(s.mongo_uri),
                "db_name": s.mongo_db_name,
            },
        )
        raise

    db = client[s.mongo_db_name]
    _mongo = Mongo(client=client, db=db)

    log.info(
        "MongoDB connected",
        extra={
            "mongo_uri": _mask_mongo_uri(s.mongo_uri),
            "db_name": s.mongo_db_name,
        },
    )

    return _mongo


def get_db() -> Database:
    if not _mongo:
        connect()
    return _mongo.db  # type: ignore[return-value]


def close() -> None:
    global _mongo
    if _mongo:
        try:
            _mongo.client.close()
            log.info("MongoDB connection closed")
        finally:
            _mongo = None