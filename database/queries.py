"""Database functions for each epic in userStories.md. Call these from your Flask/FastAPI routes.

Account, sign-in and profile functions are in accounts.py.

    from database import get_db, queries
    queries.nearby_stops(get_db(), lat=40.7553, lon=-73.9871, step_free=True)
"""
import secrets
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

NYC = ZoneInfo("America/New_York")
WALK_M_PER_MIN = 80              # ~4.8 km/h, used to turn walking minutes into a search radius
KG_CO2_PER_GALLON = 8.887        # EPA: CO2 from burning one gallon of gasoline
KM_PER_MILE = 1.609344

DEFAULT_PREFERENCES = {
    "theme": "system", "text_scale": 1.0, "color_vision": "default", "reduce_motion": "system",
    "step_free": False, "avoid_stairs_and_steep": False, "include_bike_legs": True,
    "temperature_unit": "F", "show_tips": True, "show_carbon_goals": True, "comparison_vehicle": "car_gasoline",
}


def now() -> datetime:
    return datetime.now(timezone.utc)


def oid(value) -> ObjectId:
    return value if isinstance(value, ObjectId) else ObjectId(value)


def clean(doc):
    """Make a document JSON-safe for API responses (ObjectId -> str, recursively)."""
    if isinstance(doc, list):
        return [clean(d) for d in doc]
    if isinstance(doc, dict):
        return {k: clean(v) for k, v in doc.items()}
    if isinstance(doc, ObjectId):
        return str(doc)
    return doc


def _near(lat, lon, max_meters):
    return {"$nearSphere": {"$geometry": {"type": "Point", "coordinates": [lon, lat]}, "$maxDistance": max_meters}}


def _with_distance(db, coll, lat, lon, max_meters, query, limit):
    """$geoNear aggregation: returns docs nearest first with distance_m and walk_minutes added."""
    return clean(list(db[coll].aggregate([
        {"$geoNear": {"near": {"type": "Point", "coordinates": [lon, lat]}, "distanceField": "distance_m",
                      "maxDistance": max_meters, "query": query, "spherical": True}},
        {"$limit": limit},
        {"$addFields": {"walk_minutes": {"$ceil": {"$divide": ["$distance_m", WALK_M_PER_MIN]}}}},
    ])))


# =============================================================================== DATA FRESHNESS
# Real-Time S5, Crowding S4, Bikes S2, Weather S4

def source_status(db, key):
    """{"status", "last_success_at", "is_stale"} for a feed such as "mta_gtfs_rt" or "citibike_gbfs"."""
    s = db.data_sources.find_one({"key": key}) or {}
    last = s.get("last_success_at")
    if last and last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)
    stale = last is None or (now() - last).total_seconds() > s.get("stale_after_seconds", 300)
    return {"key": key, "status": s.get("status", "down"), "last_success_at": last,
            "is_stale": stale, "last_error": s.get("last_error")}


def record_source_result(db, key, ok, error=None, name=None, stale_after_seconds=None):
    """Call this from each feed-import job after it runs. `name` is required by the validator the first time."""
    t = now()
    update = {"last_attempt_at": t, "status": "ok" if ok else "down", "last_error": None if ok else str(error)}
    if ok:
        update["last_success_at"] = t
    if stale_after_seconds is not None:
        update["stale_after_seconds"] = stale_after_seconds
    db.data_sources.update_one({"key": key}, {"$set": update, "$setOnInsert": {"name": name or key}}, upsert=True)


# =============================================================================== MAP / STOPS / ALERTS

def nearby_stops(db, lat, lon, max_meters=800, mode=None, step_free=False, limit=20):
    """Nearby Stops, Map S2. Nearest first, with distance_m and walk_minutes."""
    q = {}
    if mode:
        q["mode"] = mode
    if step_free:
        q["wheelchair_accessible"] = True
    return _with_distance(db, "stops", lat, lon, max_meters, q, limit)


def search_stops(db, text, limit=10):
    """Trip Planner S1: suggestions as you type (stops only; use a geocoder for addresses)."""
    return clean(list(db.stops.find({"$text": {"$search": text}}, {"score": {"$meta": "textScore"}})
                      .sort([("score", {"$meta": "textScore"})]).limit(limit)))


def stop_details(db, stop_id):
    """Stop screen: info + active alerts + crowding + elevator/escalator outages (Accessibility S4)."""
    stop = db.stops.find_one({"stop_id": stop_id})
    if not stop:
        return None
    stop["alerts"] = active_alerts(db, stop_ids=[stop_id], route_ids=stop.get("route_ids"))
    stop["crowding"] = current_crowding(db, stop_id)
    stop["equipment_outages"] = [e for e in stop.get("equipment", []) if not e.get("in_service")]
    return clean(stop)


def map_layer(db, agency):
    """Map S1, S3: every station and line of one agency (e.g. "LIRR"), for drawing the whole network."""
    stops = db.stops.find({"agency": agency}, {"_id": 0, "stop_id": 1, "name": 1, "location": 1,
                                               "route_ids": 1, "wheelchair_accessible": 1}).sort("name", 1)
    routes = db.routes.find({"agency": agency}, {"_id": 0, "route_id": 1, "short_name": 1, "long_name": 1,
                                                 "color": 1, "text_color": 1, "shape": 1})
    return {"stops": list(stops), "routes": list(routes)}


def _active_period_filter(t):
    return {"active_periods": {"$elemMatch": {"start": {"$lte": t}, "$or": [{"end": None}, {"end": {"$gt": t}}]}}}


def active_alerts(db, route_ids=None, stop_ids=None):
    """Real-Time S3: alerts in effect right now, optionally for given lines/stops."""
    q = _active_period_filter(now())
    targets = []
    if route_ids:
        targets.append({"route_ids": {"$in": list(route_ids)}})
    if stop_ids:
        targets.append({"stop_ids": {"$in": list(stop_ids)}})
    if targets:
        q = {"$and": [q, {"$or": targets}]}
    return clean(list(db.service_alerts.find(q).sort("active_periods.start", -1)))


def alerts_list(db, route_id=None):
    """Real-Time S3: alerts screen, split into current disruptions and planned work."""
    t = now()
    base = {"route_ids": route_id} if route_id else {}
    current = list(db.service_alerts.find({**base, **_active_period_filter(t), "is_planned": False}))
    planned = list(db.service_alerts.find({**base, "is_planned": True,
                                           "$or": [{"active_periods.end": None}, {"active_periods.end": {"$gt": t}}]})
                   .sort("active_periods.start", 1))
    return {"current": clean(current), "planned": clean(planned),
            "source": source_status(db, "mta_alerts")}


# =============================================================================== CROWDING

def current_crowding(db, stop_id):
    """Crowding S1, S4: live if there's a reading in the last 2 hours, else estimated from the
    typical pattern, else unavailable (never a guessed value)."""
    live = db.crowding_reports.find_one({"stop_id": stop_id}, sort=[("reported_at", -1)])
    if live:
        return {"stop_id": stop_id, "level": live["level"], "kind": "live", "updated_at": live["reported_at"]}
    local = now().astimezone(NYC)
    day_type = "weekend" if local.weekday() >= 5 else "weekday"
    pattern = db.crowding_patterns.find_one({"stop_id": stop_id, "day_type": day_type})
    level = pattern["hourly"][local.hour] if pattern else None
    if level is None:
        return {"stop_id": stop_id, "level": None, "kind": "unavailable", "updated_at": None}
    return {"stop_id": stop_id, "level": level, "kind": "estimated", "updated_at": pattern.get("updated_at"),
            "method": pattern.get("method")}


def crowding_for_stops(db, stop_ids):
    """Crowding S1: levels for many stops at once (map markers, stops along a route)."""
    return {sid: current_crowding(db, sid) for sid in stop_ids}


def typical_crowding(db, stop_id, day_type):
    """Crowding S2: 24 hourly levels for "weekday" or "weekend"."""
    return clean(db.crowding_patterns.find_one({"stop_id": stop_id, "day_type": day_type}))


def expected_crowding(db, stop_id, when: datetime):
    """Crowding S2: expected level for a future planned trip."""
    local = when.astimezone(NYC)
    p = db.crowding_patterns.find_one({"stop_id": stop_id, "day_type": "weekend" if local.weekday() >= 5 else "weekday"})
    return p["hourly"][local.hour] if p else None


def report_crowding(db, stop_id, level, route_id=None):
    """Anonymous rider report; disappears after 2 hours."""
    doc = {"stop_id": stop_id, "level": level, "kind": "rider_report", "reported_at": now()}
    if route_id:
        doc["route_id"] = route_id
    db.crowding_reports.insert_one(doc)


# =============================================================================== BIKES

def nearby_bike_stations(db, lat, lon, max_meters=800, need=None, limit=20, low_threshold=3):
    """Bikes S1, S2. need = "bikes" | "docks" | "ebikes" | None. Offline stations are labeled and
    never shown as having bikes or docks."""
    q = {}
    if need == "bikes":
        q = {"status": "active", "is_renting": True, "bikes_available": {"$gt": 0}}
    elif need == "ebikes":
        q = {"status": "active", "is_renting": True, "ebikes_available": {"$gt": 0}}
    elif need == "docks":
        q = {"status": "active", "is_returning": True, "docks_available": {"$gt": 0}}
    stations = _with_distance(db, "bike_stations", lat, lon, max_meters, q, limit)
    for s in stations:
        if s["status"] != "active":
            s.update(available=False, bikes_available=None, ebikes_available=None, docks_available=None)
        else:
            s["available"] = True
            s["low_bikes"] = s.get("bikes_available", 0) <= low_threshold
            s["low_docks"] = s.get("docks_available", 0) <= low_threshold
    return {"stations": stations, "source": source_status(db, "citibike_gbfs")}


# =============================================================================== PLACES

def is_open_now(hours, at=None):
    """Hours are local NYC "HH:MM" per weekday (0 = Monday). Handles closing after midnight."""
    if not hours:
        return None
    local = (at or now()).astimezone(NYC)
    hm = local.strftime("%H:%M")
    for h in hours:
        if h["day"] == local.weekday():
            if h["open"] <= h["close"] and h["open"] <= hm < h["close"]:
                return True
            if h["open"] > h["close"] and hm >= h["open"]:
                return True
        if h["day"] == (local.weekday() - 1) % 7 and h["open"] > h["close"] and hm < h["close"]:
            return True
    return False


def nearby_places(db, lat, lon, categories=None, max_walk_minutes=15, min_rating=None, price_levels=None,
                  lodging_only=False, open_now=False, limit=30):
    """Nearby Stops S1, S2, Local Businesses S1, S2. Nearest first."""
    q = {}
    if categories:
        q["category"] = {"$in": list(categories)}
    if lodging_only:
        q["is_lodging"] = True
    if min_rating is not None:
        q["rating"] = {"$gte": min_rating}
    if price_levels:
        q["price_level"] = {"$in": list(price_levels)}
    places = _with_distance(db, "businesses", lat, lon, max_walk_minutes * WALK_M_PER_MIN, q, limit * 2)
    for p in places:
        p["open_now"] = is_open_now(p.get("hours"))
    if open_now:
        places = [p for p in places if p["open_now"]]
    return places[:limit]


def place_details(db, place_id):
    """Local Businesses S3, Nearby Stops S5."""
    p = db.businesses.find_one({"_id": oid(place_id)})
    if p:
        p["open_now"] = is_open_now(p.get("hours"))
    return clean(p)


def search_places(db, text, limit=10):
    return clean(list(db.businesses.find({"$text": {"$search": text}}).limit(limit)))


# =============================================================================== WEATHER

def area_key(lat, lon):
    return f"{round(lat, 2):.2f},{round(lon, 2):.2f}"


def cached_weather(db, lat, lon):
    """Weather S1-S4: returns the cached report (< 30 min old) or None, meaning call the weather API
    and then save_weather()."""
    return clean(db.weather_cache.find_one({"area_key": area_key(lat, lon)}))


def save_weather(db, lat, lon, current, hourly=(), daily=(), alerts=(), source="weather_api"):
    db.weather_cache.update_one({"area_key": area_key(lat, lon)}, {"$set": {
        "location": {"type": "Point", "coordinates": [lon, lat]}, "fetched_at": now(), "source": source,
        "current": current, "hourly": list(hourly)[:48], "daily": list(daily), "alerts": list(alerts)}}, upsert=True)
    record_source_result(db, "weather", True)


def c_to_f(c):
    return round(c * 9 / 5 + 32)


# =============================================================================== EMERGENCY

def emergency_info(db):
    """Emergency S1, S4: public help contacts in display order, with the last update time."""
    items = list(db.emergency_info.find().sort("order", 1))
    last = max((i.get("updated_at") for i in items if i.get("updated_at")), default=None)
    return {"items": clean(items), "updated_at": last}


def upsert_emergency_info(db, admin_id, item):
    """Emergency S4: admin edit; takes effect without an app release."""
    item = {**item, "updated_at": now(), "updated_by": oid(admin_id)}
    db.emergency_info.update_one({"key": item["key"]}, {"$set": item}, upsert=True)


# =============================================================================== CARBON

def emissions_for_legs(db, legs, vehicle_key="car_gasoline"):
    """Carbon S1, S3: per-leg CO2, total, the car comparison and % saved."""
    factors = {f["key"]: f for f in db.emission_factors.find()}
    by_mode = {f["mode"]: f for f in factors.values() if f["kind"] != "vehicle"}
    vehicle = factors.get(vehicle_key) or next((f for f in factors.values() if f.get("is_default_comparison")), None)
    car_factor = vehicle["kg_co2_per_km"] if vehicle else 0.19
    out_legs, total, km = [], 0.0, 0.0
    for leg in legs:
        f = by_mode.get(leg["mode"], {}).get("kg_co2_per_km", 0)
        co2 = round(leg["distance_km"] * f, 3)
        out_legs.append({**leg, "co2_kg": co2})
        total += co2
        km += leg["distance_km"]
    car = round(km * car_factor, 3)
    return {
        "legs": out_legs, "co2_kg": round(total, 3), "car_co2_kg": car,
        "co2_avoided_kg": round(car - total, 3),
        "percent_saved": round(100 * (car - total) / car) if car else 0,
        "comparison_vehicle": vehicle["key"] if vehicle else vehicle_key,
        "factors_version": f'{vehicle["source"]} {vehicle["year"]}' if vehicle else "unknown",
    }


def carbon_summary(db, user_id, since=None):
    """Carbon S2: totals for a time range, in relatable terms too. since=None means all time."""
    match = {"user_id": oid(user_id), "status": "completed"}
    if since:
        match["depart_at"] = {"$gte": since}
    r = next(db.trips.aggregate([
        {"$match": match},
        {"$group": {"_id": None, "trips": {"$sum": 1}, "km": {"$sum": "$total_distance_km"},
                    "co2_kg": {"$sum": "$co2_kg"}, "co2_avoided_kg": {"$sum": "$co2_avoided_kg"},
                    "car_free_trips": {"$sum": 1}}},
    ]), None)
    if not r:
        return {"trips": 0, "message": "Your carbon summary is built from trips you complete in the app."}
    return {
        "trips": r["trips"], "km": round(r["km"], 2), "co2_kg": round(r["co2_kg"], 2),
        "co2_avoided_kg": round(r["co2_avoided_kg"], 2),
        "miles_not_driven": round(r["km"] / KM_PER_MILE, 1),
        "gallons_avoided": round(r["co2_avoided_kg"] / KG_CO2_PER_GALLON, 2),
        "is_estimate": True,
    }


def carbon_trend(db, user_id, since, bucket="week"):
    """Carbon S2: totals per week or month, for a chart (and a text table alternative)."""
    fmt = "%G-W%V" if bucket == "week" else "%Y-%m"
    return list(db.trips.aggregate([
        {"$match": {"user_id": oid(user_id), "status": "completed", "depart_at": {"$gte": since}}},
        {"$group": {"_id": {"$dateToString": {"format": fmt, "date": "$depart_at", "timezone": "America/New_York"}},
                    "co2_kg": {"$sum": "$co2_kg"}, "co2_avoided_kg": {"$sum": "$co2_avoided_kg"}, "trips": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
    ]))


def carbon_goal_progress(db, user_id):
    """Carbon S4."""
    user = db.users.find_one({"_id": oid(user_id)}, {"carbon_goal": 1})
    goal = (user or {}).get("carbon_goal")
    if not goal:
        return None
    s = carbon_summary(db, user_id, since=goal.get("starts_at"))
    value = s.get("co2_avoided_kg", 0) if goal["kind"] == "co2_avoided_kg" else s.get("trips", 0)
    done = value >= goal["target"]
    if done and not goal.get("achieved_at"):
        db.users.update_one({"_id": oid(user_id)}, {"$set": {"carbon_goal.achieved_at": now()}})
    return {"goal": goal, "value": value, "percent": min(100, round(100 * value / goal["target"])) if goal["target"] else 100,
            "achieved": done}


# =============================================================================== TRIPS (planner + history)

def save_trip(db, user_id, origin, destination, legs, depart_at, status="planned", label=None,
              time_mode="depart_at", reminder_minutes_before=None, is_favorite=False):
    """Trip Planner S4 (status="planned") or Trip History (status="completed").
    Fills in totals and carbon numbers from the legs."""
    user = db.users.find_one({"_id": oid(user_id)}, {"preferences.comparison_vehicle": 1}) or {}
    vehicle = user.get("preferences", {}).get("comparison_vehicle", "car_gasoline")
    e = emissions_for_legs(db, legs, vehicle)
    minutes = sum(l.get("duration_min", 0) for l in legs)
    transit_legs = [l for l in legs if l["mode"] not in ("walk", "bike")]
    doc = {
        "user_id": oid(user_id), "status": status, "origin": origin, "destination": destination,
        "legs": e["legs"], "depart_at": depart_at, "arrive_at": depart_at + timedelta(minutes=minutes),
        "time_mode": time_mode, "total_minutes": minutes,
        "walking_minutes": sum(l.get("duration_min", 0) for l in legs if l["mode"] == "walk"),
        "transfers": max(0, len(transit_legs) - 1),
        "total_distance_km": round(sum(l["distance_km"] for l in legs), 3),
        "fare_usd": round(sum(l.get("fare_usd", 0) for l in legs), 2),
        "co2_kg": e["co2_kg"], "car_co2_kg": e["car_co2_kg"], "co2_avoided_kg": e["co2_avoided_kg"],
        "comparison_vehicle": e["comparison_vehicle"], "emission_factors_version": e["factors_version"],
        "is_favorite": is_favorite, "notifications_enabled": status == "planned",
        "reminder_minutes_before": reminder_minutes_before, "affected_by_alert_ids": [], "ticket_ids": [],
        "created_at": now(), "updated_at": now(),
    }
    if label:
        doc["label"] = label
    return str(db.trips.insert_one(doc).inserted_id)


def validate_trip_date(when: datetime):
    """Trip Planner S2: not in the past, no more than 30 days ahead. Returns an error message or None."""
    t = now()
    if when < t - timedelta(minutes=5):
        return "Trips can't be planned in the past."
    if when > t + timedelta(days=30):
        return "Trips can be planned up to 30 days ahead."
    return None


def upcoming_trips(db, user_id):
    """Trip Planner S4: saved future trips in date order, with any active alerts on their lines (S5)."""
    trips = list(db.trips.find({"user_id": oid(user_id), "status": "planned", "depart_at": {"$gte": now()}})
                 .sort("depart_at", 1))
    for t in trips:
        route_ids = [l["route_id"] for l in t["legs"] if l.get("route_id")]
        t["warnings"] = [a for a in alerts_affecting(db, route_ids, t["depart_at"])]
    return clean(trips)


def alerts_affecting(db, route_ids, when):
    """Alerts on these lines that are active at `when` (works for future planned work too)."""
    if not route_ids:
        return []
    return clean(list(db.service_alerts.find({"route_ids": {"$in": route_ids}, "active_periods": {"$elemMatch": {
        "start": {"$lte": when}, "$or": [{"end": None}, {"end": {"$gt": when}}]}}})))


def update_trip(db, user_id, trip_id, **fields):
    """Trip Planner S4, S5: edit date/time, notifications, reminder, favorite, label."""
    allowed = {"depart_at", "label", "notifications_enabled", "reminder_minutes_before", "is_favorite", "status"}
    sets = {k: v for k, v in fields.items() if k in allowed}
    sets["updated_at"] = now()
    return db.trips.update_one({"_id": oid(trip_id), "user_id": oid(user_id)}, {"$set": sets}).modified_count == 1


def delete_trip(db, user_id, trip_id):
    return db.trips.delete_one({"_id": oid(trip_id), "user_id": oid(user_id)}).deleted_count == 1


def clear_trip_history(db, user_id):
    """Trip History S4 / Accounts S5: clears past trips, keeps upcoming saved ones."""
    return db.trips.delete_many({"user_id": oid(user_id), "status": {"$ne": "planned"}}).deleted_count


def trip_history(db, user_id, start=None, end=None, place=None, route_id=None, mode=None, limit=50, skip=0):
    """Trip History S1, S4: newest first, with optional filters."""
    q = {"user_id": oid(user_id), "status": "completed"}
    if start or end:
        q["depart_at"] = {k: v for k, v in (("$gte", start), ("$lte", end)) if v}
    if place:
        rx = {"$regex": place, "$options": "i"}
        q["$or"] = [{"origin.name": rx}, {"destination.name": rx}]
    if route_id:
        q["legs.route_id"] = route_id
    if mode:
        q["legs.mode"] = mode
    return clean(list(db.trips.find(q).sort("depart_at", -1).skip(skip).limit(limit)))


def favorite_trips(db, user_id):
    """Trip History S3."""
    return clean(list(db.trips.find({"user_id": oid(user_id), "is_favorite": True}).sort("updated_at", -1)))


def travel_summary(db, user_id, since=None):
    """Trip History S2: frequent routes, most-used lines, usual days/hours, monthly totals."""
    match = {"user_id": oid(user_id), "status": "completed"}
    if since:
        match["depart_at"] = {"$gte": since}
    tz = "America/New_York"
    r = next(db.trips.aggregate([
        {"$match": match},
        {"$facet": {
            "frequent_routes": [
                {"$group": {"_id": {"from": "$origin.name", "to": "$destination.name"}, "trips": {"$sum": 1}}},
                {"$sort": {"trips": -1}}, {"$limit": 5}],
            "top_lines": [
                {"$unwind": "$legs"}, {"$match": {"legs.route_id": {"$exists": True}}},
                {"$group": {"_id": "$legs.route_id", "trips": {"$sum": 1}}}, {"$sort": {"trips": -1}}, {"$limit": 5}],
            "by_weekday": [
                {"$group": {"_id": {"$isoDayOfWeek": {"date": "$depart_at", "timezone": tz}}, "trips": {"$sum": 1}}},
                {"$sort": {"_id": 1}}],
            "by_hour": [
                {"$group": {"_id": {"$hour": {"date": "$depart_at", "timezone": tz}}, "trips": {"$sum": 1}}},
                {"$sort": {"trips": -1}}, {"$limit": 3}],
            "monthly": [
                {"$group": {"_id": {"$dateToString": {"format": "%Y-%m", "date": "$depart_at", "timezone": tz}},
                            "trips": {"$sum": 1}, "fare_usd": {"$sum": "$fare_usd"}}},
                {"$sort": {"_id": -1}}],
        }},
    ]), {})
    r["fare_amounts_are_simulated"] = True
    return r


def suggested_trip(db, user_id):
    """Trip History S3: most frequent completed route, offered on app open."""
    top = travel_summary(db, user_id, since=now() - timedelta(days=60)).get("frequent_routes", [])
    return top[0] if top and top[0]["trips"] >= 3 else None


# =============================================================================== TICKETS (simulated)

def fare_products(db, include_reduced=True):
    """Ticketing S1."""
    q = {"active": True}
    if not include_reduced:
        q["reduced_fare"] = False
    return clean(list(db.fare_products.find(q).sort("sort_order", 1)))


DECLINE_LAST4 = {"0002"}   # Stripe's test card 4000 0000 0000 0002 always declines


def purchase_tickets(db, user_id, items, method_id, idempotency_key, trip_id=None):
    """Ticketing S2. items = [{"fare_code": "single", "quantity": 2}].
    The same idempotency_key always returns the same order, so a retry never charges twice.
    Generate the key in the frontend when the order summary is shown."""
    existing = db.orders.find_one({"idempotency_key": idempotency_key})
    if existing:
        return clean(existing)

    user = db.users.find_one({"_id": oid(user_id)}, {"payment_methods": 1})
    method = next((m for m in user.get("payment_methods", []) if m["id"] == method_id), None) if user else None
    products = {p["code"]: p for p in db.fare_products.find({"code": {"$in": [i["fare_code"] for i in items]}, "active": True})}

    lines = []
    for i in items:
        p = products.get(i["fare_code"])
        if not p:
            raise ValueError(f"Unknown fare: {i['fare_code']}")
        lines.append({"fare_code": p["code"], "name": p["name"], "quantity": int(i["quantity"]),
                      "unit_price_usd": p["price_usd"]})
    total = round(sum(l["quantity"] * l["unit_price_usd"] for l in lines), 2)

    order = {"user_id": oid(user_id), "idempotency_key": idempotency_key, "items": lines, "total_usd": total,
             "simulated": True, "created_at": now(), "receipt_number": None, "failure_reason": None}
    if trip_id:
        order["trip_id"] = oid(trip_id)
    if not method:
        order.update(status="failed", failure_reason="Choose a saved test payment method.")
    else:
        order["payment"] = {"method_id": method["id"], "brand": method["brand"], "last4": method["last4"],
                            "reference": "sim_" + secrets.token_hex(8)}
        if method["last4"] in DECLINE_LAST4:
            order.update(status="failed", failure_reason="Your (test) card was declined. Try another test card.")
        else:
            order.update(status="succeeded", completed_at=now(),
                         receipt_number="TH-" + now().strftime("%Y%m%d") + "-" + secrets.token_hex(3).upper())
    try:
        order_id = db.orders.insert_one(order).inserted_id
    except DuplicateKeyError:          # two identical requests raced; return the winner
        return clean(db.orders.find_one({"idempotency_key": idempotency_key}))

    if order["status"] == "succeeded":
        tickets = []
        for l in lines:
            p = products[l["fare_code"]]
            for _ in range(l["quantity"]):
                tickets.append({"user_id": oid(user_id), "order_id": order_id, "fare_code": p["code"],
                                "fare_name": p["name"], "status": "ready", "code": "TH" + secrets.token_hex(10).upper(),
                                "rides_remaining": p.get("rides"), "purchased_at": now(), "activated_at": None,
                                "valid_until": None, "refund": None, "simulated": True})
        ids = db.tickets.insert_many(tickets).inserted_ids
        if trip_id:
            db.trips.update_one({"_id": oid(trip_id)}, {"$push": {"ticket_ids": {"$each": ids}}})
    order["_id"] = order_id
    return clean(order)


def _expire_tickets(db, user_id):
    db.tickets.update_many({"user_id": oid(user_id), "status": "active", "valid_until": {"$lt": now()}},
                           {"$set": {"status": "expired"}})


def user_tickets(db, user_id):
    """Ticketing S3, S4: active/ready tickets separated from used/expired/refunded."""
    _expire_tickets(db, user_id)
    all_t = list(db.tickets.find({"user_id": oid(user_id)}).sort("purchased_at", -1))
    return {"current": clean([t for t in all_t if t["status"] in ("ready", "active")]),
            "past": clean([t for t in all_t if t["status"] not in ("ready", "active")])}


def validate_ticket(db, user_id, ticket_id):
    """Ticketing S3: demo validation. First tap activates the ticket; rides are counted down."""
    t = db.tickets.find_one({"_id": oid(ticket_id), "user_id": oid(user_id)})
    if not t or t["status"] not in ("ready", "active"):
        return clean(t)
    product = db.fare_products.find_one({"code": t["fare_code"]}) or {}
    sets = {}
    if t["status"] == "ready":
        sets.update(status="active", activated_at=now())
        if product.get("validity_days"):
            sets["valid_until"] = now() + timedelta(days=product["validity_days"])
    rides = t.get("rides_remaining")
    if rides is not None:
        sets["rides_remaining"] = rides - 1
        if rides - 1 <= 0:
            sets["status"] = "used"
    return clean(db.tickets.find_one_and_update({"_id": t["_id"]}, {"$set": sets}, return_document=ReturnDocument.AFTER))


def request_refund(db, user_id, ticket_id, reason=""):
    """Ticketing S4: only unused tickets are eligible."""
    res = db.tickets.update_one(
        {"_id": oid(ticket_id), "user_id": oid(user_id), "status": "ready", "refund": None},
        {"$set": {"refund": {"status": "requested", "reason": reason, "requested_at": now(), "resolved_at": None}}})
    return res.modified_count == 1


def purchase_history(db, user_id):
    """Ticketing S4 / Accounts S4: each charge with date, simulated amount and receipt."""
    return clean(list(db.orders.find({"user_id": oid(user_id)}).sort("created_at", -1)))


# =============================================================================== ONBOARDING & HELP

def walkthrough(db, paths=(), include_tips=False):
    """Onboarding S1, S3: steps for everyone plus steps for the chosen paths, in order."""
    q = {"$or": [{"paths": {"$size": 0}}, {"paths": {"$exists": False}}, {"paths": {"$in": list(paths)}}]}
    if not include_tips:
        q["is_tip"] = {"$ne": True}
    steps = list(db.tutorial_steps.find(q).sort("order", 1))
    last = max((s.get("updated_at") for s in steps if s.get("updated_at")), default=None)
    return {"steps": clean(steps), "total": len(steps), "updated_at": last}


def help_topics(db, feature=None):
    """Onboarding S2: topics organized by feature."""
    q = {"published": True}
    if feature:
        q["feature"] = feature
    return clean(list(db.help_topics.find(q, {"body": 0}).sort([("feature", 1), ("title", 1)])))


def search_help(db, text, limit=10):
    """Onboarding S2: matches first; if nothing matches, suggest the most helpful topics."""
    res = list(db.help_topics.find({"$text": {"$search": text}, "published": True}, {"score": {"$meta": "textScore"}})
               .sort([("score", {"$meta": "textScore"})]).limit(limit))
    log_event(db, "help_search", query=text[:100])
    if res:
        return {"results": clean(res), "suggestions": []}
    return {"results": [], "suggestions": clean(list(db.help_topics.find({"published": True})
                                                     .sort("helpful_count", -1).limit(5)))}


def help_feedback(db, slug, helpful: bool):
    """Onboarding S4: anonymous helpful / not helpful."""
    db.help_topics.update_one({"slug": slug}, {"$inc": {"helpful_count" if helpful else "not_helpful_count": 1}})
    log_event(db, "help_feedback", topic_slug=slug, helpful=helpful)


def create_support_request(db, user_id, kind, message, subject=""):
    """Onboarding S2."""
    t = now()
    return str(db.support_requests.insert_one({"user_id": oid(user_id), "kind": kind, "subject": subject,
                                               "message": message, "status": "open", "admin_reply": None,
                                               "created_at": t, "updated_at": t}).inserted_id)


def log_event(db, event, **fields):
    """Onboarding S4, Emergency S4: anonymous usage event. Never pass user ids or personal data."""
    fields.pop("user_id", None)
    db.usage_events.insert_one({"event": event, "at": now(), **fields})


def usage_report(db, since):
    """Onboarding S4: admin report of events, top help topics, and where people skip the walkthrough."""
    return {
        "events": list(db.usage_events.aggregate([
            {"$match": {"at": {"$gte": since}}}, {"$group": {"_id": "$event", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}])),
        "skipped_at_step": list(db.usage_events.aggregate([
            {"$match": {"at": {"$gte": since}, "event": "walkthrough_skipped"}},
            {"$group": {"_id": "$step_key", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}])),
        "top_topics": list(db.usage_events.aggregate([
            {"$match": {"at": {"$gte": since}, "event": "help_topic_viewed"}},
            {"$group": {"_id": "$topic_slug", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}, {"$limit": 10}])),
    }


# =============================================================================== NOTIFICATIONS

def _in_quiet_hours(quiet, at):
    if not quiet:
        return False
    hm = at.astimezone(NYC).strftime("%H:%M")
    s, e = quiet["start"], quiet["end"]
    return s <= hm < e if s <= e else (hm >= s or hm < e)


def users_to_notify_for_alert(db, alert):
    """Real-Time S4, Trip Planner S5, Accessibility S4: users who follow an affected line or station,
    or have an upcoming trip on it. Respects chosen types and quiet hours."""
    ntype = {"delay": "delay", "cancellation": "cancellation", "elevator_outage": "elevator_outage",
             "escalator_outage": "elevator_outage"}.get(alert["effect"], "service_change")
    t = now()
    follower_q = {"notifications.enabled": True, "notifications.types": ntype,
                  "$or": [{"notifications.followed_route_ids": {"$in": alert.get("route_ids", [])}},
                          {"notifications.followed_stop_ids": {"$in": alert.get("stop_ids", [])}}]}
    user_ids = {u["_id"] for u in db.users.find(follower_q, {"_id": 1})}
    trip_users = db.trips.distinct("user_id", {"status": "planned", "notifications_enabled": True,
                                               "depart_at": {"$gte": t},
                                               "legs.route_id": {"$in": alert.get("route_ids", [])}})
    user_ids.update(trip_users)
    result = []
    for u in db.users.find({"_id": {"$in": list(user_ids)}, "notifications.enabled": True}, {"notifications": 1}):
        n = u.get("notifications", {})
        if u["_id"] not in trip_users and ntype not in n.get("types", []):
            continue
        if _in_quiet_hours(n.get("quiet_hours"), t):
            continue
        result.append(u["_id"])
    return result, ntype


def create_notification(db, user_id, type_, title, body="", link="", alert_id=None, trip_id=None):
    """Stores the notification (in-app inbox). Returns None if this user was already notified about
    this alert. Send the push separately using users.notifications.devices."""
    doc = {"user_id": oid(user_id), "type": type_, "title": title, "body": body, "link": link,
           "pushed_at": None, "read_at": None, "created_at": now()}
    if alert_id:
        doc["alert_id"] = alert_id
    if trip_id:
        doc["trip_id"] = oid(trip_id)
    try:
        return str(db.notifications.insert_one(doc).inserted_id)
    except DuplicateKeyError:
        return None


def due_trip_reminders(db):
    """Trip Planner S5: planned trips whose reminder time has arrived and hasn't been sent yet.
    Run from a scheduled job every minute or so."""
    t = now()
    out = []
    for trip in db.trips.find({"status": "planned", "notifications_enabled": True,
                               "reminder_minutes_before": {"$ne": None}, "reminder_sent_at": {"$in": [None]},
                               "depart_at": {"$gt": t, "$lte": t + timedelta(hours=24)}}):
        if trip["depart_at"] - timedelta(minutes=trip["reminder_minutes_before"]) <= t:
            out.append(trip)
    return out
