"""Fast tests that run without a real MongoDB (uses mongomock).

    pip install -r requirements-dev.txt
    pytest -q

mongomock can't run geo queries ($geoNear), $text search or $facet, and it doesn't enforce
validators or partial indexes. The validators are checked here with tests/schema_check.py instead;
geo/text/facet functions are tested against Atlas by running `python -m database.init_db --seed`.
"""
from datetime import timedelta

import mongomock
import pytest

from database import accounts as a
from database import queries as q
from database import seed as seed_module
from database.schemas import COLLECTIONS
from schema_check import errors


@pytest.fixture()
def db(monkeypatch):
    db = mongomock.MongoClient()["transithub_test"]
    for name, spec in COLLECTIONS.items():
        db.create_collection(name)
        for ix in spec["indexes"]:
            d = ix.document
            if "partialFilterExpression" in d or "sparse" in d:
                continue
            db[name].create_index(list(d["key"].items()), unique=d.get("unique", False))

    def upsert(coll, key, docs):          # mongomock's bulk_write doesn't support newer PyMongo
        for doc in docs:
            coll.update_one({key: doc[key]}, {"$set": doc}, upsert=True)

    monkeypatch.setattr(seed_module, "_upsert", upsert)
    seed_module.seed(db)
    return db


@pytest.fixture()
def demo(db):
    return db.users.find_one({"email": "demo@transithub.test"})["_id"]


def test_seed_matches_validators(db):
    seed_module.seed(db)  # second run must not duplicate or break anything
    problems = [(n, e) for n, s in COLLECTIONS.items() for d in db[n].find()
                for e in errors(d, s["validator"]["$jsonSchema"])]
    assert problems == []
    assert db.users.count_documents({}) == 2


def test_crowding_live_estimated_unavailable(db):
    assert q.current_crowding(db, "127")["kind"] == "live"
    assert q.current_crowding(db, "A27")["kind"] == "estimated"
    assert q.current_crowding(db, "401234") == {"stop_id": "401234", "level": None, "kind": "unavailable",
                                                "updated_at": None}


def test_alerts_split_current_and_planned(db):
    r = q.alerts_list(db, "A")
    assert [x["alert_id"] for x in r["current"]] == ["sample-elevator-1"]
    assert [x["alert_id"] for x in r["planned"]] == ["sample-planned-1"]


def test_emissions_and_summary(db, demo):
    e = q.emissions_for_legs(db, [{"mode": "subway", "distance_km": 10}, {"mode": "walk", "distance_km": 1}])
    assert e["co2_kg"] == pytest.approx(0.58)
    assert e["legs"][1]["co2_kg"] == 0
    assert 0 < e["percent_saved"] < 100
    s = q.carbon_summary(db, demo)
    assert s["trips"] == 3 and s["co2_avoided_kg"] > 0


def test_trip_date_limits():
    assert q.validate_trip_date(q.now() + timedelta(days=31))
    assert q.validate_trip_date(q.now() - timedelta(days=1))
    assert q.validate_trip_date(q.now() + timedelta(days=3)) is None


def test_upcoming_trip_gets_planned_work_warning(db, demo):
    trips = q.upcoming_trips(db, demo)
    assert len(trips) == 1 and trips[0]["warnings"][0]["alert_id"] == "sample-planned-1"


def test_purchase_is_idempotent_and_test_cards_only(db, demo):
    first = q.purchase_tickets(db, demo, [{"fare_code": "single", "quantity": 1}], "pm_demo_visa", "k1")
    again = q.purchase_tickets(db, demo, [{"fare_code": "single", "quantity": 1}], "pm_demo_visa", "k1")
    assert first["_id"] == again["_id"] and first["status"] == "succeeded"
    with pytest.raises(a.AccountError):
        a.add_payment_method(db, demo, "4111 1111 1111 1112", 1, 2030)
    declining = a.add_payment_method(db, demo, "4000 0000 0000 0002", 1, 2030)
    assert q.purchase_tickets(db, demo, [{"fare_code": "7day", "quantity": 1}], declining, "k2")["status"] == "failed"


def test_ticket_lifecycle_and_refund(db, demo):
    tickets = q.user_tickets(db, demo)["current"]
    assert q.validate_ticket(db, demo, tickets[0]["_id"])["status"] == "used"   # single ride
    assert q.request_refund(db, demo, tickets[1]["_id"])
    assert not q.request_refund(db, demo, tickets[0]["_id"])                   # used: not eligible


def test_account_flow(db):
    with pytest.raises(a.AccountError):
        a.create_user(db, "x@y.com", "short", "X")
    uid, token = a.create_user(db, "New@Example.com", "goodpass123", "New")
    with pytest.raises(a.AccountError):
        a.create_user(db, "new@example.com", "goodpass123", "Dup")
    with pytest.raises(a.AccountError, match="verify"):
        a.sign_in(db, "new@example.com", "goodpass123")
    a.verify_email(db, token)
    session, user = a.sign_in(db, "new@example.com", "goodpass123")
    assert "password_hash" not in user
    assert a.user_from_session(db, session)["email"] == "new@example.com"
    a.sign_out(db, session)
    assert a.user_from_session(db, session) is None


def test_lockout_after_five_failures(db):
    uid, token = a.create_user(db, "lock@example.com", "goodpass123", "L")
    a.verify_email(db, token)
    for _ in range(5):
        with pytest.raises(a.AccountError):
            a.sign_in(db, "lock@example.com", "wrong-pass-1")
    with pytest.raises(a.AccountError, match="Too many"):
        a.sign_in(db, "lock@example.com", "goodpass123")


def test_primary_contact_first(db, demo):
    a.add_emergency_contact(db, demo, "Zed", "+1-555-0199", is_primary=True)
    assert a.emergency_contacts(db, demo)[0]["name"] == "Zed"


def test_delete_account_removes_everything(db, demo):
    counts = a.delete_account(db, demo)
    assert counts["users"] == 1
    assert all(db[c].count_documents({"user_id": demo}) == 0 for c in ("trips", "orders", "tickets"))
