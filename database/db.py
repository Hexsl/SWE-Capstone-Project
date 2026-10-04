"""MongoDB connection for TransitHub NYC.

Works with both Flask and FastAPI. Import `get_db()` anywhere you need the database:

    from database.db import get_db
    db = get_db()
    db.stops.find_one({"stop_id": "127"})
"""
import os
from functools import lru_cache

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGODB_DB", "transithub")


@lru_cache(maxsize=1)
def get_client() -> MongoClient:
    """One shared client per process (PyMongo pools connections internally)."""
    return MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000, tz_aware=True)


def get_db() -> Database:
    return get_client()[DB_NAME]


def ping() -> bool:
    """Quick health check, e.g. for a /health route."""
    get_client().admin.command("ping")
    return True
