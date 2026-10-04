"""Collection definitions for TransitHub NYC: a $jsonSchema validator and the indexes for each.

Built from userStories.md. Comments name the epic and story each collection or field serves,
e.g. "Accounts S4" = User Accounts, Story 4. See docs/DATABASE.md for the full mapping.

Validation is "moderate": documents that existed before a schema change are not rejected.
"""
from pymongo import ASCENDING, DESCENDING, GEOSPHERE, TEXT, IndexModel

# ------------------------------------------------------------------ schema helpers
STR = {"bsonType": "string"}
BOOL = {"bsonType": "bool"}
DATE = {"bsonType": "date"}
OID = {"bsonType": "objectId"}
INT = {"bsonType": "int"}
NUM = {"bsonType": ["double", "int", "long", "decimal"]}
MONEY = {"bsonType": ["decimal", "double", "int"], "minimum": 0}


def opt(schema):
    """Same type, or null."""
    if "enum" in schema:
        return {**schema, "enum": schema["enum"] + [None]}
    t = schema["bsonType"]
    return {**schema, "bsonType": (t if isinstance(t, list) else [t]) + ["null"]}


def enum(*values):
    return {"enum": list(values)}


def arr(items, **kw):
    return {"bsonType": "array", "items": items, **kw}


def obj(required=(), **props):
    s = {"bsonType": "object", "properties": props}
    if required:
        s["required"] = list(required)
    return s


def num(minimum=None, maximum=None):
    s = dict(NUM)
    if minimum is not None:
        s["minimum"] = minimum
    if maximum is not None:
        s["maximum"] = maximum
    return s


def collection(required, **props):
    return {"$jsonSchema": obj(required, **props)}


# GeoJSON point: coordinates are [longitude, latitude]
POINT = obj(["type", "coordinates"], type=enum("Point"),
            coordinates=arr(num(), minItems=2, maxItems=2))
PLACE = obj(["name", "location"], name=STR, address=STR, location=POINT,
            business_id=OID, stop_id=STR)

TRANSIT_MODES = ["subway", "bus", "rail", "ferry"]
LEG_MODES = TRANSIT_MODES + ["walk", "bike"]
CROWDING = ["low", "moderate", "high"]
BUSINESS_CATEGORIES = ["hotel", "hostel", "motel", "bnb", "restaurant", "cafe", "attraction", "park",
                       "shopping", "grocery", "pharmacy", "atm", "other"]
LODGING = ["hotel", "hostel", "motel", "bnb"]
USE_PATHS = ["commuter", "visitor", "accessibility", "cyclist"]
NOTIFICATION_TYPES = ["delay", "cancellation", "service_change", "elevator_outage", "trip_change",
                      "trip_reminder", "severe_weather", "carbon_goal"]

# One leg of a trip (Trip Planner S3, Map S3, Carbon S1, Bikes S4)
LEG = obj(
    ["mode", "distance_km"],
    mode=enum(*LEG_MODES),
    route_id=STR, line_name=STR, direction=STR,
    from_stop_id=STR, to_stop_id=STR,
    from_station_id=STR, to_station_id=STR,          # bike legs
    from_name=STR, to_name=STR,
    depart_at=DATE, arrive_at=DATE,
    distance_km=num(0), duration_min=num(0),
    fare_usd=MONEY,
    co2_kg=num(0),
    path=obj(["type", "coordinates"], type=enum("LineString"), coordinates=arr(arr(NUM))),
    steps=arr(obj(["instruction"], instruction=STR, distance_m=num(0))),
    step_free=BOOL,
)

# Shared "where did this data come from and how fresh is it" fields (Real-Time S5, Crowding S4, Bikes S2, Weather S4)
FRESHNESS = {"source": STR, "updated_at": DATE}


COLLECTIONS = {
    # ================================================================== USER ACCOUNTS
    "users": {
        "validator": collection(
            ["email", "password_hash", "display_name", "role", "created_at"],
            email=STR,                                     # stored lower-case; unique index below
            email_verified=BOOL,                           # Accounts S1
            pending_email=opt(STR),                        # Accounts S3: new email waits for verification
            password_hash=STR,                             # bcrypt; never plain text
            display_name={"bsonType": "string", "minLength": 1},
            phone=opt(STR),
            role=enum("user", "admin"),                    # admin: Emergency S4, Onboarding S4
            security=obj(
                failed_logins=INT, locked_until=opt(DATE), # Accounts S2: lockout after repeated failures
                password_changed_at=DATE,
            ),

            # Themes & Accessibility S1, S2, S4, S5
            preferences=obj(
                theme=enum("system", "light", "dark", "high_contrast"),
                text_scale=num(1, 2),
                color_vision=enum("default", "protanopia", "deuteranopia", "tritanopia"),
                reduce_motion=enum("system", "on", "off"),
                step_free=BOOL,
                avoid_stairs_and_steep=BOOL,
                include_bike_legs=BOOL,                    # Bikes S4
                temperature_unit=enum("F", "C"),           # Weather S1
                show_tips=BOOL,                            # Onboarding S2
                show_carbon_goals=BOOL,                    # Carbon S4
                comparison_vehicle=STR,                    # Carbon S3: emission_factors.key, e.g. "car_gasoline"
            ),

            # Real-Time S4, Trip Planner S5, Accessibility S4, Weather S3
            notifications=obj(
                enabled=BOOL,
                types=arr(enum(*NOTIFICATION_TYPES)),
                quiet_hours=opt(obj(["start", "end"], start={"bsonType": "string", "pattern": "^[0-2][0-9]:[0-5][0-9]$"},
                                    end={"bsonType": "string", "pattern": "^[0-2][0-9]:[0-5][0-9]$"})),
                followed_route_ids=arr(STR),
                followed_stop_ids=arr(STR),                # stations whose elevator outages to report
                devices=arr(obj(["token", "platform"], token=STR, platform=enum("ios", "android", "web"),
                                added_at=DATE)),
            ),

            # Accounts S4: simulated payment methods. Test cards only, never a full card number.
            payment_methods=arr(obj(
                ["id", "brand", "last4", "is_test"],
                id=STR, brand=STR, last4={"bsonType": "string", "pattern": "^[0-9]{4}$"},
                exp_month=num(1, 12), exp_year=num(2024, 2100), is_default=BOOL,
                is_test=enum(True), label=STR,
            )),

            # Emergency S2
            emergency_contacts=arr(obj(
                ["id", "name", "phone"],
                id=STR, name=STR, phone=STR, relationship=STR, is_primary=BOOL,
            )),

            saved_places=arr(PLACE),                       # Local Businesses S4
            onboarding=obj(                                # Onboarding S1, S3
                walkthrough_completed=BOOL, walkthrough_completed_at=opt(DATE),
                accessibility_prompt_seen=BOOL,
                paths=arr(enum(*USE_PATHS)),
                dismissed_tips=arr(STR),
            ),
            carbon_goal=opt(obj(                           # Carbon S4
                ["kind", "target", "period"],
                kind=enum("co2_avoided_kg", "car_free_trips"), target=num(0),
                period=enum("week", "month", "year"), starts_at=DATE, achieved_at=opt(DATE),
            )),
            created_at=DATE, updated_at=DATE,
        ),
        "indexes": [
            IndexModel([("email", ASCENDING)], unique=True),
            IndexModel([("pending_email", ASCENDING)], unique=True,
                       partialFilterExpression={"pending_email": {"$type": "string"}}),
        ],
    },

    # Accounts S1, S2, S3: email verification, password reset, email change. Only a hash of the token is stored.
    "auth_tokens": {
        "validator": collection(
            ["user_id", "purpose", "token_hash", "expires_at"],
            user_id=OID, purpose=enum("verify_email", "reset_password", "change_email"),
            token_hash=STR, email=STR, expires_at=DATE, used_at=opt(DATE), created_at=DATE,
        ),
        "indexes": [
            IndexModel([("token_hash", ASCENDING)], unique=True),
            IndexModel([("user_id", ASCENDING), ("purpose", ASCENDING)]),
            IndexModel([("expires_at", ASCENDING)], expireAfterSeconds=0),     # deleted when expired
        ],
    },

    # Accounts S2: "remain signed in on that device until I sign out"
    "sessions": {
        "validator": collection(
            ["user_id", "token_hash", "created_at", "expires_at"],
            user_id=OID, token_hash=STR, device=STR, created_at=DATE, last_seen_at=DATE, expires_at=DATE,
        ),
        "indexes": [
            IndexModel([("token_hash", ASCENDING)], unique=True),
            IndexModel([("user_id", ASCENDING)]),
            IndexModel([("expires_at", ASCENDING)], expireAfterSeconds=0),
        ],
    },

    # ================================================================== TRANSIT DATA (MTA GTFS)
    # Map S1-S4, Nearby Stops S3, Accessibility S4, Crowding S1
    "stops": {
        "validator": collection(
            ["stop_id", "name", "mode", "location"],
            stop_id=STR, name=STR, mode=enum(*TRANSIT_MODES),
            parent_station_id=opt(STR),
            location=POINT,
            route_ids=arr(STR),
            borough=enum("Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"),
            wheelchair_accessible=BOOL,
            exits=arr(obj(["name"], name=STR, location=POINT, step_free=BOOL)),     # Nearby Stops S4
            equipment=arr(obj(                                                     # Accessibility S4
                ["equipment_id", "type", "in_service"],
                equipment_id=STR, type=enum("elevator", "escalator"), description=STR,
                in_service=BOOL, outage_until=opt(DATE), updated_at=DATE,
            )),
            **FRESHNESS,
        ),
        "indexes": [
            IndexModel([("stop_id", ASCENDING)], unique=True),
            IndexModel([("location", GEOSPHERE)]),
            IndexModel([("route_ids", ASCENDING)]),
            IndexModel([("name", TEXT)]),
        ],
    },

    "routes": {
        "validator": collection(
            ["route_id", "short_name", "mode"],
            route_id=STR, short_name=STR, long_name=STR, mode=enum(*TRANSIT_MODES),
            color={"bsonType": "string", "pattern": "^#[0-9A-Fa-f]{6}$"},
            text_color={"bsonType": "string", "pattern": "^#[0-9A-Fa-f]{6}$"},
            directions=arr(obj(["direction_id", "headsign", "stop_ids"],
                               direction_id=enum(0, 1), headsign=STR, stop_ids=arr(STR))),
            shape=obj(["type", "coordinates"], type=enum("LineString", "MultiLineString"), coordinates=arr({})),
            **FRESHNESS,
        ),
        "indexes": [IndexModel([("route_id", ASCENDING)], unique=True), IndexModel([("mode", ASCENDING)])],
    },

    # Real-Time S3: reroutes, skipped stops, planned work; also feeds Trip Planner S5 and Accessibility S4
    "service_alerts": {
        "validator": collection(
            ["alert_id", "header", "effect", "severity", "is_planned", "active_periods"],
            alert_id=STR, header=STR, description=STR,
            effect=enum("delay", "cancellation", "reroute", "skipped_stops", "reduced_service",
                        "planned_work", "elevator_outage", "escalator_outage", "major_incident", "other"),
            severity=enum("info", "warning", "severe"),
            is_planned=BOOL,                                   # S3: planned work shown apart from current disruptions
            route_ids=arr(STR), stop_ids=arr(STR),
            active_periods=arr(obj(["start"], start=DATE, end=opt(DATE)), minItems=1),
            safety_instructions=opt(STR),                      # Emergency S3
            **FRESHNESS,
        ),
        "indexes": [
            IndexModel([("alert_id", ASCENDING)], unique=True),
            # route_ids and active_periods are both arrays; MongoDB can't put two arrays in one index
            IndexModel([("route_ids", ASCENDING)]),
            IndexModel([("stop_ids", ASCENDING)]),
            IndexModel([("active_periods.end", ASCENDING)]),
        ],
    },

    # Real-Time S5, Crowding S4, Bikes S2, Weather S4, Emergency S4: last update and health of each feed
    "data_sources": {
        "validator": collection(
            ["key", "name", "status"],
            key=STR, name=STR, url=STR,
            status=enum("ok", "stale", "down"),
            last_success_at=opt(DATE), last_attempt_at=opt(DATE), last_error=opt(STR),
            stale_after_seconds=INT,
        ),
        "indexes": [IndexModel([("key", ASCENDING)], unique=True)],
    },

    # ================================================================== CROWDING
    # Crowding S1, S4: live readings and rider reports. Removed after 2 hours.
    "crowding_reports": {
        "validator": collection(
            ["stop_id", "level", "kind", "reported_at"],
            stop_id=STR, route_id=STR, level=enum(*CROWDING),
            kind=enum("live_feed", "rider_report"),
            reported_at=DATE,
            # deliberately no user_id: riders' reports stay anonymous
        ),
        "indexes": [
            IndexModel([("stop_id", ASCENDING), ("reported_at", DESCENDING)]),
            IndexModel([("reported_at", ASCENDING)], expireAfterSeconds=2 * 60 * 60),
        ],
    },

    # Crowding S2, S4: typical crowding by stop, day type and hour (the "estimated" values)
    "crowding_patterns": {
        "validator": collection(
            ["stop_id", "day_type", "hourly"],
            stop_id=STR, day_type=enum("weekday", "weekend"),
            hourly=arr(enum(*CROWDING, None), minItems=24, maxItems=24),   # index 0 = midnight; null = no data
            method=STR,                                                    # S4: "how it is measured"
            **FRESHNESS,
        ),
        "indexes": [IndexModel([("stop_id", ASCENDING), ("day_type", ASCENDING)], unique=True)],
    },

    # ================================================================== TRIPS
    # Trip Planner S4, S5 (saved upcoming trips), Trip History S1-S4, Accounts S5, Carbon S1, S2
    "trips": {
        "validator": collection(
            ["user_id", "status", "origin", "destination", "legs", "depart_at", "created_at"],
            user_id=OID,
            status=enum("planned", "completed", "cancelled"),
            origin=PLACE, destination=PLACE,
            legs=arr(LEG, minItems=1),
            depart_at=DATE, arrive_at=DATE,
            time_mode=enum("depart_at", "arrive_by", "now"),        # Trip Planner S2
            total_minutes=num(0), walking_minutes=num(0), transfers=num(0),
            total_distance_km=num(0),
            fare_usd=MONEY,                                         # simulated
            co2_kg=num(0), car_co2_kg=num(0), co2_avoided_kg=num(),  # Carbon S1, S2
            comparison_vehicle=STR,                                 # Carbon S3: vehicle used for car_co2_kg
            emission_factors_version=STR,                           # Carbon S3: source + year used
            is_favorite=BOOL, label=STR,                            # Trip History S3
            # Trip Planner S4, S5: saved future trips
            notifications_enabled=BOOL, reminder_minutes_before=opt(INT), reminder_sent_at=opt(DATE),
            affected_by_alert_ids=arr(STR),
            ticket_ids=arr(OID),
            created_at=DATE, updated_at=DATE,
        ),
        "indexes": [
            IndexModel([("user_id", ASCENDING), ("status", ASCENDING), ("depart_at", DESCENDING)]),
            IndexModel([("user_id", ASCENDING), ("is_favorite", ASCENDING)]),
            IndexModel([("status", ASCENDING), ("depart_at", ASCENDING)]),   # reminder job: upcoming planned trips
            IndexModel([("legs.route_id", ASCENDING), ("status", ASCENDING)]),  # alerts that affect saved trips
        ],
    },

    # ================================================================== TICKETING (all simulated)
    # Ticketing S1: catalog of fares (admin-editable, so prices aren't hard-coded)
    "fare_products": {
        "validator": collection(
            ["code", "name", "price_usd", "active"],
            code=STR, name=STR, description=STR,
            price_usd=MONEY, rides=opt(INT), validity_days=opt(INT),
            reduced_fare=BOOL, eligibility=opt(STR),
            modes=arr(enum(*TRANSIT_MODES)),
            active=BOOL, sort_order=INT,
        ),
        "indexes": [IndexModel([("code", ASCENDING)], unique=True), IndexModel([("active", ASCENDING), ("sort_order", ASCENDING)])],
    },

    # Ticketing S2, S4, Accounts S4: one document per checkout. The idempotency key keeps a retry
    # from charging twice.
    "orders": {
        "validator": collection(
            ["user_id", "idempotency_key", "items", "total_usd", "status", "simulated", "created_at"],
            user_id=OID,
            idempotency_key=STR,
            items=arr(obj(["fare_code", "quantity", "unit_price_usd"],
                          fare_code=STR, name=STR, quantity=num(1, 20), unit_price_usd=MONEY), minItems=1),
            total_usd=MONEY,
            status=enum("pending", "succeeded", "failed", "refunded", "partially_refunded"),
            failure_reason=opt(STR),
            payment=obj(["method_id", "brand", "last4"], method_id=STR, brand=STR,
                        last4={"bsonType": "string", "pattern": "^[0-9]{4}$"}, reference=STR),
            receipt_number=opt(STR),
            simulated=enum(True),
            trip_id=opt(OID),                 # Ticketing S1: came from a planned trip
            created_at=DATE, completed_at=opt(DATE),
        ),
        "indexes": [
            IndexModel([("idempotency_key", ASCENDING)], unique=True),
            IndexModel([("user_id", ASCENDING), ("created_at", DESCENDING)]),
            IndexModel([("receipt_number", ASCENDING)], unique=True,
                       partialFilterExpression={"receipt_number": {"$type": "string"}}),
        ],
    },

    # Ticketing S3, S4: one document per ticket
    "tickets": {
        "validator": collection(
            ["user_id", "order_id", "fare_code", "status", "code", "purchased_at"],
            user_id=OID, order_id=OID, fare_code=STR, fare_name=STR,
            status=enum("ready", "active", "used", "expired", "refunded"),
            code=STR,                                       # value for the scannable-style code
            rides_remaining=opt(INT),
            purchased_at=DATE, activated_at=opt(DATE), valid_until=opt(DATE),
            refund=opt(obj(["status", "requested_at"],     # Ticketing S4
                           status=enum("requested", "approved", "denied", "completed"),
                           reason=STR, requested_at=DATE, resolved_at=opt(DATE))),
            simulated=enum(True),
        ),
        "indexes": [
            IndexModel([("user_id", ASCENDING), ("status", ASCENDING), ("purchased_at", DESCENDING)]),
            IndexModel([("code", ASCENDING)], unique=True),
            IndexModel([("order_id", ASCENDING)]),
        ],
    },

    # ================================================================== BIKES (Citi Bike GBFS)
    # Bikes S1-S4
    "bike_stations": {
        "validator": collection(
            ["station_id", "name", "location", "status"],
            station_id=STR, name=STR, location=POINT,
            capacity=num(0), bikes_available=num(0), ebikes_available=num(0), docks_available=num(0),
            status=enum("active", "offline", "out_of_service"),
            is_renting=BOOL, is_returning=BOOL,
            rental_url=STR,                                   # S3: hand off to the provider's app
            last_reported=DATE,
            **FRESHNESS,
        ),
        "indexes": [
            IndexModel([("station_id", ASCENDING)], unique=True),
            IndexModel([("location", GEOSPHERE)]),
        ],
    },

    # ================================================================== PLACES
    # Local Businesses S1-S3, Nearby Stops S1, S2, S5
    "businesses": {
        "validator": collection(
            ["name", "category", "location", "source"],
            name=STR, category=enum(*BUSINESS_CATEGORIES),
            is_lodging=BOOL,
            location=POINT, address=STR, neighborhood=STR,
            phone=opt(STR), website=opt(STR),
            rating=opt(num(0, 5)), review_count=opt(INT), price_level=opt(num(1, 4)),
            # Opening hours per weekday: 0 = Monday. Times are "HH:MM" local; close < open means past midnight.
            hours=arr(obj(["day", "open", "close"], day=num(0, 6), open=STR, close=STR)),
            nearest_stops=arr(obj(["stop_id", "walk_minutes"], stop_id=STR, name=STR,
                                  route_ids=arr(STR), walk_minutes=num(0))),
            source=enum("yelp", "osm", "manual"), external_id=STR,
            updated_at=DATE,
        ),
        "indexes": [
            IndexModel([("location", GEOSPHERE)]),
            IndexModel([("category", ASCENDING), ("rating", DESCENDING)]),
            IndexModel([("source", ASCENDING), ("external_id", ASCENDING)], unique=True),
            IndexModel([("name", TEXT), ("neighborhood", TEXT)]),
        ],
    },

    # ================================================================== WEATHER
    # Weather S1-S4. Cached per area so the weather API isn't hit on every page load.
    # Temperatures are stored in Celsius and converted for display.
    "weather_cache": {
        "validator": collection(
            ["area_key", "location", "fetched_at", "current"],
            area_key=STR,                   # lat/lon rounded to 2 decimals, e.g. "40.76,-73.99"
            location=POINT,
            fetched_at=DATE,
            current=obj(["temp_c", "conditions"], temp_c=NUM, feels_like_c=NUM, conditions=STR,
                        precip_mm=num(0), precip_chance=num(0, 100), wind_kph=num(0), wind_dir=STR),
            hourly=arr(obj(["time", "temp_c"], time=DATE, temp_c=NUM, conditions=STR, precip_chance=num(0, 100))),
            daily=arr(obj(["date", "high_c", "low_c"], date=DATE, high_c=NUM, low_c=NUM, conditions=STR,
                          precip_chance=num(0, 100))),
            alerts=arr(obj(["event", "severity"], event=STR, severity=STR, headline=STR, starts=DATE, ends=opt(DATE))),
            source=STR,
        ),
        "indexes": [
            IndexModel([("area_key", ASCENDING)], unique=True),
            IndexModel([("fetched_at", ASCENDING)], expireAfterSeconds=30 * 60),
        ],
    },

    # ================================================================== EMERGENCY
    # Emergency S1, S3, S4: public help contacts and safety instructions, admin-editable
    "emergency_info": {
        "validator": collection(
            ["key", "name", "category", "when_to_use", "order"],
            key=STR, name=STR,
            category=enum("emergency", "transit", "city_services", "accessibility", "crisis", "instructions"),
            phone=opt(STR), sms=opt(STR), url=opt(STR),
            when_to_use=STR,
            order=INT,
            updated_at=DATE, updated_by=opt(OID),
        ),
        "indexes": [IndexModel([("key", ASCENDING)], unique=True), IndexModel([("order", ASCENDING)])],
    },

    # ================================================================== CARBON
    # Carbon S1, S3: kg CO2 per passenger-km for each mode and comparison vehicle, with source and year
    "emission_factors": {
        "validator": collection(
            ["key", "label", "kind", "kg_co2_per_km", "source", "year"],
            key=STR, label=STR,
            kind=enum("transit", "active", "vehicle"),
            mode=enum(*LEG_MODES, "car"),
            kg_co2_per_km=num(0),
            source=STR, year=INT, notes=STR,
            is_default_comparison=BOOL,
        ),
        "indexes": [IndexModel([("key", ASCENDING)], unique=True)],
    },

    # ================================================================== ONBOARDING & HELP
    # Onboarding S1, S3: walkthrough steps, tagged by path
    "tutorial_steps": {
        "validator": collection(
            ["key", "order", "title", "body"],
            key=STR, order=INT, title=STR, body=STR,
            feature=enum("map", "trip_planner", "live_updates", "tickets", "bikes", "weather", "emergency",
                         "places", "carbon", "accessibility", "account", "general"),
            paths=arr(enum(*USE_PATHS)),         # empty = shown to everyone
            asks_permission=opt(enum("location", "notifications")),
            image_url=opt(STR), image_alt=opt(STR),
            is_tip=BOOL,                          # S2: one-time tip shown when a feature first opens
            updated_at=DATE,
        ),
        "indexes": [IndexModel([("key", ASCENDING)], unique=True), IndexModel([("order", ASCENDING)])],
    },

    # Onboarding S2, S4: help articles, searchable, with helpful/not-helpful counts
    "help_topics": {
        "validator": collection(
            ["slug", "feature", "title", "body"],
            slug=STR, feature=STR, title=STR, body=STR, keywords=arr(STR),
            helpful_count=INT, not_helpful_count=INT,
            published=BOOL, updated_at=DATE, updated_by=opt(OID),
        ),
        "indexes": [
            IndexModel([("slug", ASCENDING)], unique=True),
            IndexModel([("title", TEXT), ("body", TEXT), ("keywords", TEXT)],
                       weights={"title": 10, "keywords": 5, "body": 1}),
            IndexModel([("feature", ASCENDING)]),
        ],
    },

    # Onboarding S2: "contact support or report a problem ... and see its status"
    "support_requests": {
        "validator": collection(
            ["user_id", "kind", "message", "status", "created_at"],
            user_id=OID, kind=enum("question", "problem", "feedback", "refund"),
            subject=STR, message=STR,
            status=enum("open", "in_progress", "resolved", "closed"),
            admin_reply=opt(STR),
            created_at=DATE, updated_at=DATE,
        ),
        "indexes": [IndexModel([("user_id", ASCENDING), ("created_at", DESCENDING)]),
                    IndexModel([("status", ASCENDING)])],
    },

    # Onboarding S4, Emergency S4: anonymous usage events. No user ids or personal data.
    # Removed after 180 days.
    "usage_events": {
        "validator": collection(
            ["event", "at"],
            event=enum("walkthrough_started", "walkthrough_step_viewed", "walkthrough_skipped",
                       "walkthrough_completed", "help_topic_viewed", "help_search", "help_feedback",
                       "tip_dismissed", "error"),
            at=DATE,
            step_key=opt(STR), topic_slug=opt(STR), query=opt(STR), helpful=opt(BOOL),
            error_code=opt(STR), app_version=opt(STR), platform=opt(STR),
        ),
        "indexes": [
            IndexModel([("event", ASCENDING), ("at", DESCENDING)]),
            IndexModel([("at", ASCENDING)], expireAfterSeconds=180 * 24 * 60 * 60),
        ],
    },

    # ================================================================== NOTIFICATIONS
    # Real-Time S4, Trip Planner S5, Weather S3, Accessibility S4, Carbon S4: in-app inbox + push log.
    # Removed after 90 days.
    "notifications": {
        "validator": collection(
            ["user_id", "type", "title", "created_at"],
            user_id=OID, type=enum(*NOTIFICATION_TYPES),
            title=STR, body=STR,
            link=STR,                         # S4: opening it goes to the alert/line/trip
            alert_id=opt(STR), trip_id=opt(OID),
            pushed_at=opt(DATE), read_at=opt(DATE), created_at=DATE,
        ),
        "indexes": [
            IndexModel([("user_id", ASCENDING), ("created_at", DESCENDING)]),
            # Never notify the same user twice about the same alert/trip
            IndexModel([("user_id", ASCENDING), ("type", ASCENDING), ("alert_id", ASCENDING), ("trip_id", ASCENDING)],
                       unique=True, partialFilterExpression={"alert_id": {"$type": "string"}}),
            IndexModel([("created_at", ASCENDING)], expireAfterSeconds=90 * 24 * 60 * 60),
        ],
    },
}

# Collections that hold one user's personal data; used to delete an account completely (Accounts S3)
USER_OWNED = ["trips", "orders", "tickets", "notifications", "support_requests", "auth_tokens", "sessions"]
