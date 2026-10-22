"""MongoDB connection for TransitHub NYC.

Works with both Flask and FastAPI. Import `get_db()` anywhere you need the database:

    from database.db import get_db
    db = get_db()
    db.stops.find_one({"stop_id": "127"})
"""
import os
from functools import lru_cache

import certifi
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGODB_DB", "transithub")


@lru_cache(maxsize=1)
def get_client() -> MongoClient:
    """One shared client per process (PyMongo pools connections internally)."""
    # Atlas uses TLS. certifi's CA bundle fixes CERTIFICATE_VERIFY_FAILED on python.org's macOS Python,
    # which ships without root certificates. Local mongodb:// stays plain (the option would turn TLS on).
    tls = {"tlsCAFile": certifi.where()} if MONGODB_URI.startswith("mongodb+srv://") else {}
    return MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000, tz_aware=True, **tls)


def get_db() -> Database:
    return get_client()[DB_NAME]


def ping() -> bool:
    """Quick health check, e.g. for a /health route."""
    get_client().admin.command("ping")
    return True
