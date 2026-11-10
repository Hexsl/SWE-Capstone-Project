"""Sample data so the team can build and demo before the real feeds (MTA GTFS, GBFS, Yelp/OSM, weather) are wired up.

Upserts on natural keys, so running it twice doesn't create duplicates.
Everything here is sample or simulated data; replace it with real feed imports later.
"""
from datetime import datetime, timedelta, timezone

import bcrypt
from pymongo import UpdateOne

from . import queries


def pt(lon: float, lat: float) -> dict:
    """GeoJSON point. Note the order: longitude first."""
    return {"type": "Point", "coordinates": [lon, lat]}


def _upsert(coll, key: str, docs: list[dict]) -> None:
    ops = [UpdateOne({key: d[key]}, {"$set": d}, upsert=True) for d in docs]
    if ops:
        coll.bulk_write(ops)
    print(f"  seeded   {coll.name:18} ({len(docs)} docs)")


def seed(db) -> None:
    now = datetime.now(timezone.utc)
    src = {"source": "sample", "updated_at": now}

    # ------------------------------------------------------------- transit
    _upsert(db.routes, "route_id", [
        {"route_id": "1", "short_name": "1", "long_name": "Broadway - 7 Avenue Local", "mode": "subway",
         "color": "#EE352E", "text_color": "#FFFFFF",
         "directions": [{"direction_id": 0, "headsign": "Uptown", "stop_ids": ["132", "128", "127"]},
                        {"direction_id": 1, "headsign": "Downtown", "stop_ids": ["127", "128", "132"]}], **src},
        {"route_id": "A", "short_name": "A", "long_name": "8 Avenue Express", "mode": "subway",
         "color": "#0039A6", "text_color": "#FFFFFF",
         "directions": [{"direction_id": 0, "headsign": "Uptown", "stop_ids": ["A32", "A28", "A27"]},
                        {"direction_id": 1, "headsign": "Downtown", "stop_ids": ["A27", "A28", "A32"]}], **src},
        {"route_id": "M15", "short_name": "M15", "long_name": "1st Av / 2nd Av", "mode": "bus",
         "color": "#00AEEF", "text_color": "#000000",
         "directions": [{"direction_id": 0, "headsign": "East Harlem", "stop_ids": ["401234", "401235"]}], **src},
    ])

    elevator = lambda eid, desc, ok: {"equipment_id": eid, "type": "elevator", "description": desc,
                                      "in_service": ok, "outage_until": None if ok else now + timedelta(days=2),
                                      "updated_at": now}
    _upsert(db.stops, "stop_id", [
        {"stop_id": "127", "name": "Times Sq - 42 St", "mode": "subway", "location": pt(-73.98714, 40.75529),
         "route_ids": ["1"], "borough": "Manhattan", "wheelchair_accessible": True,
         "exits": [{"name": "7 Av & W 42 St (NE corner)", "location": pt(-73.98680, 40.75560), "step_free": True}],
         "equipment": [elevator("EL123", "Street to mezzanine", True)], **src},
        {"stop_id": "128", "name": "34 St - Penn Station", "mode": "subway", "location": pt(-73.99106, 40.75037),
         "route_ids": ["1"], "borough": "Manhattan", "wheelchair_accessible": True, **src},
        {"stop_id": "132", "name": "14 St", "mode": "subway", "location": pt(-74.00020, 40.73783),
         "route_ids": ["1"], "borough": "Manhattan", "wheelchair_accessible": True, **src},
        {"stop_id": "A27", "name": "42 St - Port Authority Bus Terminal", "mode": "subway",
         "location": pt(-73.98973, 40.75731), "route_ids": ["A"], "borough": "Manhattan", "wheelchair_accessible": True, **src},
        {"stop_id": "A28", "name": "34 St - Penn Station", "mode": "subway", "location": pt(-73.99339, 40.75228),
         "route_ids": ["A"], "borough": "Manhattan", "wheelchair_accessible": True,
         "equipment": [elevator("EL456", "Mezzanine to downtown platform", False)], **src},
        {"stop_id": "A32", "name": "W 4 St - Washington Sq", "mode": "subway", "location": pt(-74.00057, 40.73225),
         "route_ids": ["A"], "borough": "Manhattan", "wheelchair_accessible": True, **src},
        {"stop_id": "401234", "name": "1 Av / E 14 St", "mode": "bus", "location": pt(-73.98163, 40.73177),
         "route_ids": ["M15"], "borough": "Manhattan", "wheelchair_accessible": True, **src},
        {"stop_id": "401235", "name": "1 Av / E 23 St", "mode": "bus", "location": pt(-73.97821, 40.73697),
         "route_ids": ["M15"], "borough": "Manhattan", "wheelchair_accessible": True, **src},
    ])

    _upsert(db.service_alerts, "alert_id", [
        {"alert_id": "sample-delay-1", "header": "Delays on the 1 train",
         "description": "Trains are running with delays because of a signal problem at 96 St.",
         "effect": "delay", "severity": "warning", "is_planned": False, "route_ids": ["1"], "stop_ids": [],
         "active_periods": [{"start": now - timedelta(minutes=20), "end": None}], **src},
        {"alert_id": "sample-elevator-1", "header": "Elevator out of service at 34 St - Penn Station",
         "description": "The elevator between the mezzanine and the downtown A platform is out of service.",
         "effect": "elevator_outage", "severity": "info", "is_planned": False, "route_ids": ["A"], "stop_ids": ["A28"],
         "active_periods": [{"start": now - timedelta(hours=3), "end": now + timedelta(days=2)}], **src},
        {"alert_id": "sample-planned-1", "header": "Weekend: A trains skip 34 St - Penn Station",
         "effect": "skipped_stops", "severity": "warning", "is_planned": True, "route_ids": ["A"], "stop_ids": ["A28"],
         "active_periods": [{"start": now + timedelta(days=5), "end": now + timedelta(days=7)}], **src},
    ])

    _upsert(db.data_sources, "key", [
        {"key": "mta_gtfs_rt", "name": "MTA real-time feeds", "status": "ok", "last_success_at": now,
         "last_attempt_at": now, "last_error": None, "stale_after_seconds": 120},
        {"key": "mta_alerts", "name": "MTA service alerts", "status": "ok", "last_success_at": now,
         "last_attempt_at": now, "last_error": None, "stale_after_seconds": 300},
        {"key": "citibike_gbfs", "name": "Citi Bike station status", "status": "ok", "last_success_at": now,
         "last_attempt_at": now, "last_error": None, "stale_after_seconds": 120},
        {"key": "weather", "name": "Weather service", "status": "ok", "last_success_at": now,
         "last_attempt_at": now, "last_error": None, "stale_after_seconds": 1800},
        {"key": "crowding", "name": "Crowding data", "status": "ok", "last_success_at": now,
         "last_attempt_at": now, "last_error": None, "stale_after_seconds": 900},
    ])

    # ------------------------------------------------------------- crowding
    L, M, H, N = "low", "moderate", "high", None
    weekday = [L, L, L, L, L, L, M, H, H, M, M, M, M, M, M, M, M, H, H, M, M, L, L, L]
    weekend = [L, L, L, L, L, L, L, L, L, L, M, M, M, M, M, M, M, M, M, M, L, L, L, L]
    for stop in ["127", "128", "132", "A27", "A28", "A32"]:
        for day_type, hourly in (("weekday", weekday), ("weekend", weekend)):
            db.crowding_patterns.update_one(
                {"stop_id": stop, "day_type": day_type},
                {"$set": {"hourly": hourly, "method": "Sample pattern for development. Replace with averages "
                          "of MTA ridership data by hour.", **src}},
                upsert=True)
    print("  seeded   crowding_patterns  (13 docs)")
    db.crowding_patterns.update_one({"stop_id": "401234", "day_type": "weekday"},
                                    {"$set": {"hourly": [N] * 24, "method": "No data", **src}}, upsert=True)
    if db.crowding_reports.count_documents({}) == 0:
        db.crowding_reports.insert_many([
            {"stop_id": "127", "route_id": "1", "level": "high", "kind": "live_feed", "reported_at": now},
            {"stop_id": "132", "route_id": "1", "level": "moderate", "kind": "rider_report", "reported_at": now},
        ])

    # ------------------------------------------------------------- bikes
    _upsert(db.bike_stations, "station_id", [
        {"station_id": "sample-42-8av", "name": "W 42 St & 8 Ave", "location": pt(-73.98993, 40.75757),
         "capacity": 47, "bikes_available": 12, "ebikes_available": 3, "docks_available": 32, "status": "active",
         "is_renting": True, "is_returning": True, "last_reported": now, **src},
        {"station_id": "sample-bway-36", "name": "Broadway & W 36 St", "location": pt(-73.98806, 40.75098),
         "capacity": 39, "bikes_available": 2, "ebikes_available": 0, "docks_available": 37, "status": "active",
         "is_renting": True, "is_returning": True, "last_reported": now, **src},
        {"station_id": "sample-13-7av", "name": "W 13 St & 7 Ave", "location": pt(-73.99979, 40.73782),
         "capacity": 33, "bikes_available": 30, "ebikes_available": 4, "docks_available": 1, "status": "active",
         "is_renting": True, "is_returning": True, "last_reported": now, **src},
        {"station_id": "sample-offline", "name": "W 41 St & 9 Ave (offline sample)", "location": pt(-73.99150, 40.75820),
         "capacity": 30, "bikes_available": 0, "ebikes_available": 0, "docks_available": 0, "status": "offline",
         "is_renting": False, "is_returning": False, "last_reported": now - timedelta(hours=6), **src},
    ])

    # ------------------------------------------------------------- places
    daily = lambda o, c: [{"day": d, "open": o, "close": c} for d in range(7)]
    _upsert(db.businesses, "external_id", [
        {"name": "Sample Midtown Hotel", "category": "hotel", "is_lodging": True, "location": pt(-73.98650, 40.75600),
         "address": "W 43 St, New York, NY", "neighborhood": "Midtown", "phone": "+1-212-555-0101",
         "website": "https://example.com/hotel", "rating": 4.2, "review_count": 812, "price_level": 3,
         "hours": daily("00:00", "23:59"),
         "nearest_stops": [{"stop_id": "127", "name": "Times Sq - 42 St", "route_ids": ["1"], "walk_minutes": 2}],
         "source": "manual", "external_id": "sample-hotel-1", "updated_at": now},
        {"name": "Sample Hostel Chelsea", "category": "hostel", "is_lodging": True, "location": pt(-73.99700, 40.74500),
         "address": "W 24 St, New York, NY", "neighborhood": "Chelsea", "rating": 3.9, "price_level": 1,
         "hours": daily("00:00", "23:59"), "source": "manual", "external_id": "sample-hostel-1", "updated_at": now},
        {"name": "Sample Pizza Shop", "category": "restaurant", "is_lodging": False, "location": pt(-73.99050, 40.75100),
         "address": "W 34 St, New York, NY", "neighborhood": "Midtown", "rating": 4.5, "price_level": 1,
         "hours": daily("11:00", "02:00"),
         "nearest_stops": [{"stop_id": "128", "name": "34 St - Penn Station", "route_ids": ["1"], "walk_minutes": 1}],
         "source": "manual", "external_id": "sample-food-1", "updated_at": now},
        {"name": "Sample Pharmacy", "category": "pharmacy", "is_lodging": False, "location": pt(-73.98900, 40.75450),
         "address": "7 Ave, New York, NY", "neighborhood": "Midtown", "hours": daily("08:00", "22:00"),
         "source": "manual", "external_id": "sample-pharm-1", "updated_at": now},
        {"name": "Washington Square Park", "category": "park", "is_lodging": False, "location": pt(-73.99744, 40.73082),
         "address": "Washington Square, New York, NY", "neighborhood": "Greenwich Village", "rating": 4.7,
         "hours": daily("06:00", "00:00"),
         "nearest_stops": [{"stop_id": "A32", "name": "W 4 St - Washington Sq", "route_ids": ["A"], "walk_minutes": 4}],
         "source": "manual", "external_id": "sample-park-1", "updated_at": now},
    ])

    # ------------------------------------------------------------- weather (expires in 30 min; reseed to refresh)
    db.weather_cache.update_one({"area_key": "40.76,-73.99"}, {"$set": {
        "location": pt(-73.99, 40.76), "fetched_at": now, "source": "sample",
        "current": {"temp_c": 18.0, "feels_like_c": 17.0, "conditions": "Partly cloudy", "precip_mm": 0,
                    "precip_chance": 10, "wind_kph": 14, "wind_dir": "NW"},
        "hourly": [{"time": now + timedelta(hours=h), "temp_c": 18.0 - h * 0.2, "conditions": "Partly cloudy",
                    "precip_chance": 10} for h in range(48)],
        "daily": [{"date": (now + timedelta(days=d)).replace(hour=0, minute=0, second=0, microsecond=0),
                   "high_c": 20.0, "low_c": 12.0, "conditions": "Partly cloudy", "precip_chance": 20} for d in range(7)],
        "alerts": [],
    }}, upsert=True)
    print("  seeded   weather_cache      (1 doc, expires in 30 min)")

    # ------------------------------------------------------------- emergency
    # Numbers from nyc.gov/nypd and mta.info/agency/mta-police; re-check before release.
    _upsert(db.emergency_info, "key", [
        {"key": "911", "name": "Emergency (police, fire, ambulance)", "category": "emergency", "phone": "911",
         "sms": "911", "when_to_use": "Life-threatening emergencies or crimes in progress. You can text 911 in NYC if you can't call.",
         "order": 1, "updated_at": now},
        {"key": "nypd-non-emergency", "name": "NYPD non-emergency", "category": "police", "phone": "311",
         "url": "https://www.nyc.gov/site/nypd/about/about-nypd/contact-us.page",
         "when_to_use": "Report a crime or problem that is not an emergency, including on the subway or a bus. Call 911 if anyone is in danger.",
         "order": 2, "updated_at": now},
        {"key": "mta-police", "name": "MTA Police (LIRR, Metro-North, Staten Island Railway)", "category": "police",
         "phone": "212-878-1000", "url": "https://www.mta.info/agency/mta-police/phone-numbers",
         "when_to_use": "Report a crime or a safety concern on LIRR, Metro-North, or the Staten Island Railway, 24 hours a day. Call 911 for emergencies.",
         "order": 3, "updated_at": now},
        {"key": "disclaimer", "name": "This app does not replace emergency services", "category": "instructions",
         "when_to_use": "In an emergency, always call or text 911 first.", "order": 0, "updated_at": now},
    ])
    # Remove help numbers seeded by earlier versions (311, 511, 988, extra police lines).
    db.emergency_info.delete_many({"key": {"$nin": ["911", "nypd-non-emergency", "mta-police", "disclaimer"]}})

    # ------------------------------------------------------------- carbon
    # Approximate EPA GHG Emission Factors Hub values converted from per-mile to per-km (÷ 1.609).
    # VERIFY against the current EPA table before the final submission; EV/hybrid are placeholders.
    epa = {"source": "EPA GHG Emission Factors Hub (approx.)", "year": 2024}
    _upsert(db.emission_factors, "key", [
        {"key": "subway", "label": "Subway", "kind": "transit", "mode": "subway", "kg_co2_per_km": 0.058, **epa},
        {"key": "bus", "label": "Bus", "kind": "transit", "mode": "bus", "kg_co2_per_km": 0.044, **epa},
        {"key": "rail", "label": "Commuter rail", "kind": "transit", "mode": "rail", "kg_co2_per_km": 0.083, **epa},
        {"key": "ferry", "label": "Ferry", "kind": "transit", "mode": "ferry", "kg_co2_per_km": 0.12,
         "source": "placeholder", "year": 2024, "notes": "Replace with a sourced value"},
        {"key": "walk", "label": "Walking", "kind": "active", "mode": "walk", "kg_co2_per_km": 0.0, **epa},
        {"key": "bike", "label": "Bike", "kind": "active", "mode": "bike", "kg_co2_per_km": 0.0, **epa},
        {"key": "car_gasoline", "label": "Average gas car", "kind": "vehicle", "mode": "car", "kg_co2_per_km": 0.19,
         "is_default_comparison": True, **epa},
        {"key": "suv_gasoline", "label": "SUV / pickup", "kind": "vehicle", "mode": "car", "kg_co2_per_km": 0.25, **epa},
        {"key": "car_hybrid", "label": "Hybrid car", "kind": "vehicle", "mode": "car", "kg_co2_per_km": 0.12,
         "source": "placeholder", "year": 2024},
        {"key": "car_electric", "label": "Electric car (NY grid)", "kind": "vehicle", "mode": "car",
         "kg_co2_per_km": 0.05, "source": "placeholder", "year": 2024},
    ])

    # ------------------------------------------------------------- fares (simulated)
    # Based on 2026 MTA fares: $3.00 base, $1.50 reduced, $35 weekly cap.
    # The day pass and 30-day prices are made up for the demo.
    _upsert(db.fare_products, "code", [
        {"code": "single", "name": "Single ride", "price_usd": 3.00, "rides": 1, "validity_days": 1,
         "reduced_fare": False, "modes": ["subway", "bus"], "active": True, "sort_order": 1,
         "description": "One subway or local bus ride, with free transfers for 2 hours."},
        {"code": "day", "name": "Day pass (demo)", "price_usd": 10.00, "rides": None, "validity_days": 1,
         "reduced_fare": False, "modes": ["subway", "bus"], "active": True, "sort_order": 2},
        {"code": "7day", "name": "7-day unlimited", "price_usd": 35.00, "rides": None, "validity_days": 7,
         "reduced_fare": False, "modes": ["subway", "bus"], "active": True, "sort_order": 3},
        {"code": "30day", "name": "30-day unlimited (demo)", "price_usd": 132.00, "rides": None, "validity_days": 30,
         "reduced_fare": False, "modes": ["subway", "bus"], "active": True, "sort_order": 4},
        {"code": "single_reduced", "name": "Reduced-fare single ride", "price_usd": 1.50, "rides": 1, "validity_days": 1,
         "reduced_fare": True, "eligibility": "Riders 65+ or with a qualifying disability",
         "modes": ["subway", "bus"], "active": True, "sort_order": 5},
    ])

    # ------------------------------------------------------------- onboarding & help
    _upsert(db.tutorial_steps, "key", [
        {"key": "welcome", "order": 1, "feature": "general", "paths": [], "title": "Welcome to TransitHub NYC",
         "body": "Maps, live updates, trip planning, tickets, bikes, weather and help, all in one place.", "updated_at": now},
        {"key": "accessibility", "order": 2, "feature": "accessibility", "paths": [], "title": "Make it work for you",
         "body": "Set text size, theme, reduced motion and step-free travel now, or later in Settings.", "updated_at": now},
        {"key": "location", "order": 3, "feature": "map", "paths": [], "asks_permission": "location",
         "title": "Find stops near you",
         "body": "We use your location to show nearby stops and bikes. Everything still works if you say no.", "updated_at": now},
        {"key": "planner", "order": 4, "feature": "trip_planner", "paths": [], "title": "Plan a trip",
         "body": "Enter where you're going and pick from several route options.", "updated_at": now},
        {"key": "alerts", "order": 5, "feature": "live_updates", "paths": ["commuter"], "asks_permission": "notifications",
         "title": "Follow your lines", "body": "Get notified about delays on the lines you use. Optional.", "updated_at": now},
        {"key": "places", "order": 6, "feature": "places", "paths": ["visitor"], "title": "Explore nearby",
         "body": "Find hotels, food and attractions near any stop.", "updated_at": now},
        {"key": "stepfree", "order": 7, "feature": "accessibility", "paths": ["accessibility"], "title": "Step-free routes",
         "body": "Turn on step-free travel to avoid stairs. Elevator outages are shown on your route.", "updated_at": now},
        {"key": "bikes", "order": 8, "feature": "bikes", "paths": ["cyclist"], "title": "Bike + transit",
         "body": "See Citi Bike availability and plan trips with a bike leg.", "updated_at": now},
        {"key": "tickets", "order": 9, "feature": "tickets", "paths": [], "title": "Tickets (simulated)",
         "body": "Ticket purchases in this app are simulated. No real money is charged.", "updated_at": now},
        {"key": "emergency", "order": 10, "feature": "emergency", "paths": [], "title": "Help is one tap away",
         "body": "The help button on every screen lists emergency numbers and your own contacts.", "updated_at": now},
    ])
    _upsert(db.help_topics, "slug", [
        {"slug": "plan-a-trip", "feature": "trip_planner", "title": "How do I plan a trip?",
         "body": "Open the planner, enter a start and destination, then choose a time up to 30 days ahead.",
         "keywords": ["route", "directions", "planner"], "helpful_count": 0, "not_helpful_count": 0,
         "published": True, "updated_at": now},
        {"slug": "buy-ticket", "feature": "tickets", "title": "How do I buy a ticket?",
         "body": "Go to Tickets, choose a fare and quantity, then pay with a test card. Purchases are simulated.",
         "keywords": ["fare", "pass", "payment", "metrocard", "omny"], "helpful_count": 0, "not_helpful_count": 0,
         "published": True, "updated_at": now},
        {"slug": "crowding-explained", "feature": "crowding", "title": "How is crowding measured?",
         "body": "Live levels come from feeds and rider reports from the last two hours. When there's no live data, "
                 "we show the typical level for that hour, labeled as estimated.",
         "keywords": ["busy", "crowded", "full"], "helpful_count": 0, "not_helpful_count": 0,
         "published": True, "updated_at": now},
        {"slug": "carbon-explained", "feature": "carbon", "title": "How are carbon numbers calculated?",
         "body": "We multiply the distance of each leg by an emission factor for its mode (EPA values), "
                 "then compare with driving the same distance in the vehicle you choose.",
         "keywords": ["co2", "emissions", "environment"], "helpful_count": 0, "not_helpful_count": 0,
         "published": True, "updated_at": now},
    ])

    # ------------------------------------------------------------- demo users
    def make_user(email, name, role, **extra):
        db.users.update_one({"email": email}, {"$setOnInsert": {
            "email": email, "display_name": name, "role": role, "email_verified": True,
            "password_hash": bcrypt.hashpw(b"password123", bcrypt.gensalt()).decode(),
            "security": {"failed_logins": 0, "locked_until": None},
            "preferences": {**queries.DEFAULT_PREFERENCES},
            "notifications": {"enabled": False, "types": [], "quiet_hours": None,
                              "followed_route_ids": [], "followed_stop_ids": [], "devices": []},
            "payment_methods": [], "emergency_contacts": [], "saved_places": [],
            "onboarding": {"walkthrough_completed": False, "paths": [], "dismissed_tips": []},
            "carbon_goal": None, "created_at": now, "updated_at": now, **extra,
        }}, upsert=True)
        return db.users.find_one({"email": email}, {"_id": 1})["_id"]

    make_user("admin@transithub.test", "Admin", "admin")
    uid = make_user(
        "demo@transithub.test", "Demo Rider", "user",
        payment_methods=[{"id": "pm_demo_visa", "brand": "visa", "last4": "4242", "exp_month": 12, "exp_year": 2030,
                          "is_default": True, "is_test": True, "label": "Test Visa"}],
        emergency_contacts=[{"id": "ec_1", "name": "Alex Rider", "phone": "+1-555-0100", "relationship": "sibling",
                             "is_primary": True}],
        saved_places=[{"name": "Washington Square Park", "location": pt(-73.99744, 40.73082)}],
        carbon_goal={"kind": "co2_avoided_kg", "target": 10, "period": "month", "starts_at": now, "achieved_at": None},
    )
    print("  seeded   users              (demo@transithub.test, admin@transithub.test)")

    if db.trips.count_documents({"user_id": uid}) == 0:
        legs = [
            {"mode": "walk", "from_name": "Home", "to_name": "14 St", "distance_km": 0.3, "duration_min": 4},
            {"mode": "subway", "route_id": "1", "line_name": "1", "direction": "Uptown", "from_stop_id": "132",
             "to_stop_id": "127", "distance_km": 2.4, "duration_min": 9, "fare_usd": 3.00},
        ]
        for days_ago in (1, 3, 8):
            queries.save_trip(db, uid, status="completed",
                              origin={"name": "Home", "location": pt(-74.00020, 40.73783)},
                              destination={"name": "Times Sq - 42 St", "location": pt(-73.98714, 40.75529)},
                              legs=legs, depart_at=now - timedelta(days=days_ago, hours=2))
        queries.save_trip(db, uid, status="planned", label="Museum visit",
                          origin={"name": "Home", "location": pt(-74.00020, 40.73783)},
                          destination={"name": "34 St - Penn Station", "location": pt(-73.99339, 40.75228)},
                          legs=[{"mode": "subway", "route_id": "A", "line_name": "A", "from_stop_id": "A32",
                                 "to_stop_id": "A28", "distance_km": 2.2, "duration_min": 6, "fare_usd": 3.00}],
                          depart_at=now + timedelta(days=6), reminder_minutes_before=30)
        print("  seeded   trips              (3 past + 1 planned)")

    if db.orders.count_documents({"user_id": uid}) == 0:
        res = queries.purchase_tickets(db, uid, [{"fare_code": "single", "quantity": 2}],
                                       method_id="pm_demo_visa", idempotency_key="seed-order-1")
        print(f"  seeded   orders / tickets   ({res['status']})")
