from unittest.mock import patch

import mongomock
from rest_framework.test import APISimpleTestCase

from database import seed as seed_module
from database.schemas import COLLECTIONS

DEMO = "demo@transithub.test"
ADMIN = "admin@transithub.test"
PASSWORD = "password123"
NEW_USER = {"name": "Test Rider", "email": "rider@example.com",
            "password": "transit12345", "confirm": "transit12345"}


def make_db():
    """A fresh in-memory database with the real collections, indexes and sample data."""
    db = mongomock.MongoClient()["transithub_api_test"]
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

    with patch.object(seed_module, "_upsert", upsert):
        seed_module.seed(db)
    return db


class ApiTestCase(APISimpleTestCase):
    """Points every API module at the in-memory database."""

    def setUp(self):
        self.db = make_db()
        for target in ("backend.app.api.get_db", "backend.app.api_more.get_db",
                       "backend.app.authentication.get_db"):
            patcher = patch(target, return_value=self.db)
            patcher.start()
            self.addCleanup(patcher.stop)

    def login(self, email=DEMO, password=PASSWORD):
        """Log in through the API and send the token with every later request."""
        res = self.client.post("/api/login/", {"email": email, "password": password}, format="json")
        self.assertEqual(res.status_code, 200, res.content)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + res.json()["token"])
        return res.json()

    def signup(self, **overrides):
        return self.client.post("/api/signup/", {**NEW_USER, **overrides}, format="json")


class HealthTests(ApiTestCase):
    def test_ok_when_mongodb_reachable(self):
        with patch("backend.app.api.ping", return_value=True):
            res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"status": "ok", "mongodb": "ok"})

    def test_503_when_mongodb_down(self):
        with patch("backend.app.api.ping", side_effect=Exception("no server")):
            res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, 503)
        self.assertEqual(res.json()["mongodb"], "unreachable")


class SignupTests(ApiTestCase):
    def test_creates_verified_user_with_hashed_password(self):
        res = self.signup()
        self.assertEqual(res.status_code, 201, res.content)
        user = self.db.users.find_one({"email": "rider@example.com"})
        self.assertIsNotNone(user)
        self.assertTrue(user["email_verified"])
        self.assertNotEqual(user["password_hash"], NEW_USER["password"])
        self.assertEqual(user["display_name"], "Test Rider")

    def test_new_user_can_log_in_straight_away(self):
        self.signup()
        data = self.login("rider@example.com", NEW_USER["password"])
        self.assertEqual(data["user"]["display_name"], "Test Rider")

    def test_rejects_mismatched_passwords(self):
        res = self.signup(confirm="something-else1")
        self.assertEqual(res.status_code, 400)
        self.assertIn("do not match", res.json()["error"])
        self.assertIsNone(self.db.users.find_one({"email": "rider@example.com"}))

    def test_rejects_weak_password(self):
        res = self.signup(password="short1", confirm="short1")
        self.assertEqual(res.status_code, 400)
        self.assertIn("10 characters", res.json()["error"])

    def test_rejects_missing_name(self):
        res = self.signup(name="  ")
        self.assertEqual(res.status_code, 400)

    def test_rejects_invalid_email(self):
        res = self.signup(email="not-an-email")
        self.assertEqual(res.status_code, 400)

    def test_rejects_duplicate_email(self):
        self.assertEqual(self.signup().status_code, 201)
        res = self.signup()
        self.assertEqual(res.status_code, 400)
        self.assertIn("already exists", res.json()["error"])


class LoginTests(ApiTestCase):
    def test_login_returns_token_and_user(self):
        data = self.login()
        self.assertTrue(data["token"])
        self.assertEqual(data["user"]["email"], DEMO)
        self.assertEqual(data["user"]["role"], "user")

    def test_admin_role_is_returned(self):
        self.assertEqual(self.login(ADMIN)["user"]["role"], "admin")

    def test_wrong_password_is_rejected(self):
        res = self.client.post("/api/login/", {"email": DEMO, "password": "wrong-password1"}, format="json")
        self.assertEqual(res.status_code, 400)
        self.assertIn("incorrect", res.json()["error"])

    def test_unknown_email_gets_the_same_message(self):
        res = self.client.post("/api/login/", {"email": "nobody@example.com", "password": "x"}, format="json")
        self.assertEqual(res.status_code, 400)
        self.assertIn("incorrect", res.json()["error"])

    def test_me_requires_a_token(self):
        self.assertEqual(self.client.get("/api/me/").status_code, 401)

    def test_me_with_a_valid_token(self):
        self.login()
        res = self.client.get("/api/me/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["email"], DEMO)

    def test_a_made_up_token_is_rejected(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer not-a-real-token")
        self.assertEqual(self.client.get("/api/me/").status_code, 401)

    def test_logout_ends_the_session(self):
        self.login()
        self.assertEqual(self.client.post("/api/logout/").status_code, 200)
        self.assertEqual(self.client.get("/api/me/").status_code, 401)

    def test_account_locks_after_five_failed_attempts(self):
        for _ in range(5):
            self.client.post("/api/login/", {"email": DEMO, "password": "wrong-password1"}, format="json")
        res = self.client.post("/api/login/", {"email": DEMO, "password": PASSWORD}, format="json")
        self.assertEqual(res.status_code, 400)
        self.assertIn("Too many failed attempts", res.json()["error"])


class StopsFaresAlertsTests(ApiTestCase):
    def test_fares_lists_the_four_standard_tickets(self):
        res = self.client.get("/api/fares/")
        self.assertEqual(res.status_code, 200)
        codes = [f["code"] for f in res.json()]
        self.assertEqual(sorted(codes), ["30day", "7day", "day", "single"])
        single = next(f for f in res.json() if f["code"] == "single")
        self.assertEqual(single["price_usd"], 3.0)

    def test_nearby_stops_response_shape(self):
        fake = [{"stop_id": "127", "name": "Times Sq - 42 St", "mode": "subway", "route_ids": ["1"],
                 "walk_minutes": 1, "distance_m": 12.4, "location": {"type": "Point"}}]
        with patch("backend.app.api.queries.nearby_stops", return_value=fake) as nearby:
            res = self.client.get("/api/stops/nearby/?lat=40.7553&lon=-73.9871")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), [{"stop_id": "127", "name": "Times Sq - 42 St", "mode": "subway",
                                       "route_ids": ["1"], "walk_minutes": 1, "distance_m": 12}])
        self.assertEqual(nearby.call_args.args[1:3], (40.7553, -73.9871))

    def test_nearby_stops_defaults_to_times_square(self):
        with patch("backend.app.api.queries.nearby_stops", return_value=[]) as nearby:
            self.client.get("/api/stops/nearby/")
        self.assertEqual(nearby.call_args.args[1:3], (40.7553, -73.9871))

    def test_nearby_stops_rejects_bad_coordinates(self):
        res = self.client.get("/api/stops/nearby/?lat=abc&lon=1")
        self.assertEqual(res.status_code, 400)

    def test_alerts_split_current_and_planned(self):
        res = self.client.get("/api/alerts/")
        self.assertEqual(res.status_code, 200)
        current = [a["header"] for a in res.json()["current"]]
        planned = [a["header"] for a in res.json()["planned"]]
        self.assertIn("Delays on the 1 train", current)
        self.assertIn("Weekend: A trains skip 34 St - Penn Station", planned)
        self.assertNotIn("Weekend: A trains skip 34 St - Penn Station", current)


class PurchaseTests(ApiTestCase):
    def buy(self, key="key-1", fare="single"):
        return self.client.post("/api/purchase/", {"fare_code": fare, "idempotency_key": key}, format="json")

    def test_requires_login(self):
        self.assertEqual(self.buy().status_code, 401)

    def test_creates_an_order_and_a_ticket(self):
        self.login()
        user = self.db.users.find_one({"email": DEMO})
        tickets_before = self.db.tickets.count_documents({"user_id": user["_id"]})
        res = self.buy()
        self.assertEqual(res.status_code, 200, res.content)
        self.assertTrue(res.json()["receipt_number"].startswith("TH-"))
        self.assertEqual(res.json()["total_usd"], 3.0)
        self.assertEqual(self.db.orders.count_documents({"idempotency_key": "key-1"}), 1)
        self.assertEqual(self.db.tickets.count_documents({"user_id": user["_id"]}), tickets_before + 1)

    def test_same_key_never_charges_twice(self):
        self.login()
        first = self.buy(key="same-key")
        second = self.buy(key="same-key")
        self.assertEqual(first.json()["receipt_number"], second.json()["receipt_number"])
        self.assertEqual(self.db.orders.count_documents({"idempotency_key": "same-key"}), 1)

    def test_different_fares_have_different_totals(self):
        self.login()
        self.assertEqual(self.buy(key="a", fare="7day").json()["total_usd"], 35.0)

    def test_unknown_fare_is_rejected(self):
        self.login()
        self.assertEqual(self.buy(fare="does-not-exist").status_code, 400)

    def test_missing_fields_are_rejected(self):
        self.login()
        res = self.client.post("/api/purchase/", {"fare_code": "single"}, format="json")
        self.assertEqual(res.status_code, 400)

    def test_new_account_gets_the_test_card_and_can_buy(self):
        self.signup()
        self.login("rider@example.com", NEW_USER["password"])
        self.assertEqual(self.buy().status_code, 200)
        user = self.db.users.find_one({"email": "rider@example.com"})
        self.assertEqual(len(user["payment_methods"]), 1)
        self.assertEqual(user["payment_methods"][0]["last4"], "4242")
        self.assertTrue(user["payment_methods"][0]["is_test"])

    def test_only_the_card_brand_and_last4_are_stored(self):
        self.signup()
        self.login("rider@example.com", NEW_USER["password"])
        self.buy()
        card = self.db.users.find_one({"email": "rider@example.com"})["payment_methods"][0]
        self.assertNotIn("4242424242424242", str(card))


class TripHistoryTests(ApiTestCase):
    def test_requires_login(self):
        self.assertEqual(self.client.get("/api/trips/").status_code, 401)

    def test_demo_user_sees_their_past_trips(self):
        self.login()
        res = self.client.get("/api/trips/")
        self.assertEqual(res.status_code, 200)
        trips = res.json()
        self.assertEqual(len(trips), 3)                      # the planned trip is not history
        self.assertEqual(trips[0]["origin"], "Home")
        self.assertEqual(trips[0]["destination"], "Times Sq - 42 St")
        self.assertEqual(trips[0]["mode"], "subway")
        self.assertEqual(trips[0]["line"], "1")

    def test_mode_filter(self):
        self.login()
        self.assertEqual(len(self.client.get("/api/trips/?mode=subway").json()), 3)
        self.assertEqual(self.client.get("/api/trips/?mode=bus").json(), [])

    def test_users_cannot_see_each_others_trips(self):
        self.signup()
        self.login("rider@example.com", NEW_USER["password"])
        self.assertEqual(self.client.get("/api/trips/").json(), [])
        self.assertGreater(self.db.trips.count_documents({}), 0)   # demo's trips do exist


class AdminTests(ApiTestCase):
    def test_summary_is_forbidden_for_normal_users(self):
        self.login()
        self.assertEqual(self.client.get("/api/admin/summary/").status_code, 403)

    def test_summary_needs_login(self):
        self.assertEqual(self.client.get("/api/admin/summary/").status_code, 401)

    def test_summary_for_admin(self):
        self.login(ADMIN)
        res = self.client.get("/api/admin/summary/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["stops"], 8)
        self.assertIn("active_alerts", res.json())
        self.assertIn("reports_open", res.json())

    def test_reports_are_forbidden_for_normal_users(self):
        self.login()
        self.assertEqual(self.client.get("/api/admin/reports/").status_code, 403)

    def test_a_rider_report_reaches_the_admin(self):
        self.login()
        res = self.client.post("/api/reports/", {"kind": "problem", "subject": "Gate stuck",
                                                 "message": "The gate at Times Sq will not open."}, format="json")
        self.assertEqual(res.status_code, 201, res.content)
        self.login(ADMIN)
        reports = self.client.get("/api/admin/reports/?status=received").json()
        self.assertIn("Gate stuck", [r["subject"] for r in reports])
        self.assertGreaterEqual(self.client.get("/api/admin/summary/").json()["reports_open"], 1)

    def test_report_needs_a_message(self):
        self.login()
        res = self.client.post("/api/reports/", {"subject": "Hi", "message": "  "}, format="json")
        self.assertEqual(res.status_code, 400)

    def test_admin_can_create_an_alert_that_riders_then_see(self):
        self.login(ADMIN)
        res = self.client.post("/api/admin/alerts/", {"type": "Delay", "days": ["Monday"],
                                                      "start_time": "06:00", "end_time": "17:00"}, format="json")
        self.assertEqual(res.status_code, 201, res.content)
        self.client.credentials()          # a rider who is not logged in can still read alerts
        headers = [a["header"] for a in self.client.get("/api/alerts/").json()["current"]]
        self.assertIn("Delay on all lines", headers)

    def test_planned_work_alerts_are_listed_as_planned(self):
        self.login(ADMIN)
        self.client.post("/api/admin/alerts/", {"type": "Planned Work"}, format="json")
        self.client.credentials()
        planned = [a["header"] for a in self.client.get("/api/alerts/").json()["planned"]]
        self.assertIn("Planned Work on all lines", planned)

    def test_normal_users_cannot_create_alerts(self):
        self.login()
        res = self.client.post("/api/admin/alerts/", {"type": "Delay"}, format="json")
        self.assertEqual(res.status_code, 403)
        self.assertEqual(self.db.service_alerts.count_documents({"source": "admin"}), 0)

    def test_unknown_alert_type_is_rejected(self):
        self.login(ADMIN)
        res = self.client.post("/api/admin/alerts/", {"type": "Made Up"}, format="json")
        self.assertEqual(res.status_code, 400)