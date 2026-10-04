# TransitHub NYC – MongoDB database

The database layer for the app, built from `userStories.md`. It's plain PyMongo, so it works with Flask or FastAPI.

```
database/
  db.py        connection (reads MONGODB_URI from .env)
  schemas.py   23 collections: validation rules + indexes
  init_db.py   creates/updates collections; --seed loads sample data
  seed.py      sample NYC data, demo users
  accounts.py  sign-up, verify, sign-in/lockout, reset, profile, settings, test cards, contacts
  queries.py   everything else: map, alerts, crowding, trips, tickets, bikes, places, weather, carbon, help
tests/         pytest suite (runs without a database)
docs/DATABASE.md   which collection/function covers which user story
```

## 1. Create the Atlas cluster (one person)

1. Sign up at https://www.mongodb.com/cloud/atlas and create a free **M0** cluster.
2. **Database Access** → add a database user for each teammate ("Read and write to any database").
3. **Network Access** → add `0.0.0.0/0` (anywhere). This is fine for a class project.
4. **Connect → Drivers → Python** → copy the `mongodb+srv://...` string.

## 2. Set up locally (everyone)

From the repo root:

```bash
pip install -r requirements.txt
cp .env.example .env          # paste your connection string; .env is already in .gitignore
python -m database.init_db --seed
```

Demo logins (password `password123`): `demo@transithub.test` (rider with trips, tickets and contacts) and `admin@transithub.test` (admin).

Run the tests with `pip install -r requirements-dev.txt` and then `pytest -q`.

## 3. Use it in routes

```python
from database import get_db, queries, accounts

db = get_db()
queries.nearby_stops(db, lat=40.7553, lon=-73.9871, step_free=True)
queries.current_crowding(db, "127")          # {"level": "high", "kind": "live" | "estimated" | "unavailable", ...}
queries.alerts_list(db, route_id="A")        # {"current": [...], "planned": [...], "source": {...freshness}}
token, user = accounts.sign_in(db, email, password)
queries.purchase_tickets(db, user["_id"], [{"fare_code": "single", "quantity": 2}],
                         method_id="pm_...", idempotency_key=key_from_frontend)
```

Functions raise `accounts.AccountError` with a message that is safe to show the user. Return it as a 400 response.

## Things to know

- **GeoJSON is `[longitude, latitude]`.** Getting it backwards is the most common bug.
- **Some data deletes itself:** crowding reports after 2 h, weather after 30 min, auth tokens and sessions when they expire, notifications after 90 days, usage events after 180 days.
- **Payments are simulated.** Only Stripe test card numbers are accepted. `4242 4242 4242 4242` succeeds and `4000 0000 0000 0002` declines. Only the brand and last 4 digits are stored.
- **Passwords and tokens.** Passwords are bcrypt hashes. Session, verify and reset tokens are stored only as SHA-256 hashes, so you send the raw token in the email link or cookie.
- **Usage events are anonymous.** `usage_events` never stores a user id (Onboarding S4 and Emergency S4 ask for that).
- **Schema changes.** After editing `schemas.py`, rerun `python -m database.init_db`. It updates validators and indexes in place without deleting data.
- **Validation errors.** If an insert fails with `Document failed validation`, check `e.details["errInfo"]` to see which field.
- **Offline storage is a frontend job.** Stories that need offline access (tickets, emergency contacts, last-known info) are handled on the phone. This database is the source the app syncs from.
- **Sample data.** Fares are based on 2026 MTA prices ($3.00 base, $1.50 reduced, $35 weekly cap). The day pass and 30-day prices are made up. Emission factors are approximate EPA values; check them against the current EPA table before you submit.
