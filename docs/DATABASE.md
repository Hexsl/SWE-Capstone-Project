# Database coverage of the user stories

This maps each epic in `userStories.md` to the collections and functions that support it.
Setup instructions are in `database/README.md`.

Some acceptance criteria are frontend-only and need nothing from the database: map rendering, screen-reader labels, not relying on color alone, offline caching on the phone, and phone call/text/share sheets.

| Epic | Collections | Functions (`queries.` / `accounts.`) |
|---|---|---|
| **Interactive Map** | `stops`, `routes` (colors, directions, shape), `trips.legs[].path` | `nearby_stops`, `stop_details`, `save_trip` |
| **Real-Time Updates** | `service_alerts` (`is_planned` keeps planned work separate), `data_sources` (last updated / stale), `notifications`, `users.notifications` (types, quiet hours, followed lines) | `alerts_list`, `active_alerts`, `source_status`, `record_source_result`, `users_to_notify_for_alert`, `create_notification` |
| **Trip Planner** | `trips` with `status: "planned"`, `reminder_minutes_before`, `notifications_enabled`, `affected_by_alert_ids` | `validate_trip_date` (30-day limit), `save_trip`, `upcoming_trips` (with warnings), `update_trip`, `delete_trip`, `due_trip_reminders`, `search_stops` |
| **Nearby Stops** | `businesses` (with `nearest_stops`), `stops.exits` | `nearby_places` (category, walking-time limit), `place_details`, `nearby_stops` |
| **User Accounts** | `users`, `auth_tokens`, `sessions`, `users.payment_methods`, `orders` | `create_user`, `verify_email`, `resend_verification`, `sign_in` (5 failures → 15 min lock), `sign_out`, `request_password_reset`, `reset_password`, `update_profile` (new email verified first), `delete_account` (cascades), `add_payment_method` (test cards only), `set_default_payment_method`, `remove_payment_method` (asks for a replacement if a pass uses it), `purchase_history` |
| **Crowding** | `crowding_reports` (live, 2 h), `crowding_patterns` (typical by hour, weekday/weekend) | `current_crowding` (live → estimated → unavailable, never guessed), `crowding_for_stops`, `typical_crowding`, `expected_crowding`, `report_crowding` |
| **Themes & Accessibility** | `users.preferences` (theme incl. high contrast, text scale, color vision, reduced motion, step-free), `stops.equipment` (elevator/escalator status) | `update_preferences`, `reset_preferences`, `nearby_stops(step_free=True)`, `stop_details` (outages) |
| **Online Ticketing** | `fare_products`, `orders` (idempotency key, so no double charge), `tickets` (ready → active → used/expired, refund) | `fare_products`, `purchase_tickets`, `user_tickets`, `validate_ticket` (demo validation), `request_refund` |
| **Trip History** | `trips` with `status: "completed"`, `is_favorite` | `trip_history` (filter by date/place/line/mode), `travel_summary`, `suggested_trip`, `favorite_trips`, `clear_trip_history` |
| **Bike Locations** | `bike_stations` (status, bikes/e-bikes/docks, `rental_url`), `data_sources` | `nearby_bike_stations` (bikes/docks/e-bikes filter, low flags, offline hidden) |
| **Weather** | `weather_cache` (current, 48 h hourly, daily, alerts; 30-min cache) | `cached_weather`, `save_weather`, `c_to_f` |
| **Local Businesses** | `businesses` (lodging flag, hours, rating, price level, phone, website), `users.saved_places` | `nearby_places(lodging_only=True, open_now=True, ...)`, `place_details`, `search_places`, `save_place`, `remove_place`, `is_open_now` |
| **Emergency Contacts** | `emergency_info` (911, 311, 511, 988 + disclaimer; admin-editable), `users.emergency_contacts` (primary first) | `emergency_info`, `upsert_emergency_info`, `add/update/delete_emergency_contact`, `set_primary_contact` |
| **Carbon Footprint** | `emission_factors` (per mode and comparison vehicle, with source and year), `trips.co2_kg / car_co2_kg / co2_avoided_kg`, `users.carbon_goal` | `emissions_for_legs` (per leg, % saved), `carbon_summary` (miles not driven, gallons avoided), `carbon_trend`, `carbon_goal_progress`, `set_carbon_goal` |
| **Onboarding** | `tutorial_steps` (tagged by path), `help_topics` (text search, helpful counts), `support_requests`, `usage_events` (anonymous), `users.onboarding` | `walkthrough(paths)`, `help_topics`, `search_help` (suggestions when nothing matches), `help_feedback`, `create_support_request`, `log_event`, `usage_report`, `update_onboarding` |

## Jobs the backend still needs (not database code)

- **Feed importers** for MTA GTFS (stops, routes), GTFS-Realtime (alerts and arrivals), Citi Bike GBFS, and Yelp or OSM. Each one upserts into its collection and calls `record_source_result`.
- **A notification worker.** For each new alert it calls `users_to_notify_for_alert`, then `create_notification`, then sends the push. It also sends `due_trip_reminders` every minute.
- **An email sender** for verification and reset tokens (e.g. SendGrid, per the context diagram).
- **Live arrivals.** These are fetched from GTFS-Realtime per request and not stored, because they change every few seconds.
