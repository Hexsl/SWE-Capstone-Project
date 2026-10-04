"""User Accounts epic (S1-S5) plus the per-user settings other epics store on the user:
themes/accessibility, emergency contacts, saved places, notification settings, carbon goal, onboarding.

Tokens (sessions, email verification, password reset) are random strings. Only their SHA-256 hash
is stored, so a leaked database can't be used to sign in.
"""
import hashlib
import re
import secrets
from datetime import timedelta

import bcrypt
from pymongo.errors import DuplicateKeyError

from .queries import DEFAULT_PREFERENCES, clean, now, oid
from .schemas import USER_OWNED

MAX_FAILED_LOGINS = 5
LOCKOUT = timedelta(minutes=15)
SESSION_LIFETIME = timedelta(days=30)
TOKEN_LIFETIME = {"verify_email": timedelta(days=2), "reset_password": timedelta(hours=1),
                  "change_email": timedelta(days=2)}
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Accounts S4: only these test card numbers are accepted (Stripe's public test cards)
TEST_CARDS = {
    "4242424242424242": "visa", "4000056655665556": "visa", "5555555555554444": "mastercard",
    "378282246310005": "amex", "6011111111111117": "discover",
    "4000000000000002": "visa",   # always declines; use it to demo a failed payment
}


class AccountError(ValueError):
    """Raised with a message that is safe to show the user."""


def _hash_token(raw):
    return hashlib.sha256(raw.encode()).hexdigest()


def password_problems(pw):
    """Accounts S1: rules shown to the user. Returns a list of problems (empty = OK)."""
    problems = []
    if len(pw) < 10:
        problems.append("Use at least 10 characters.")
    if not re.search(r"[A-Za-z]", pw) or not re.search(r"\d", pw):
        problems.append("Include at least one letter and one number.")
    return problems


def public_user(user):
    """Strip secrets before sending a user to the frontend."""
    if not user:
        return None
    user = dict(user)
    user.pop("password_hash", None)
    user.pop("security", None)
    for m in user.get("payment_methods", []):
        m.pop("fingerprint", None)
    return clean(user)


# ------------------------------------------------------------------------------ sign up / verify
def create_user(db, email, password, display_name, phone=None, preferences=None, emergency_contacts=None):
    """Accounts S1. Returns (user_id, verify_token). Email the token as a link.
    preferences / emergency_contacts let a guest's on-device settings move into the new account
    (Themes S5, Emergency S2)."""
    email = email.strip().lower()
    if not EMAIL_RE.match(email):
        raise AccountError("Enter a valid email address.")
    problems = password_problems(password)
    if problems:
        raise AccountError(" ".join(problems))
    t = now()
    doc = {
        "email": email, "email_verified": False, "pending_email": None, "display_name": display_name.strip(),
        "phone": phone, "role": "user",
        "password_hash": bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode(),
        "security": {"failed_logins": 0, "locked_until": None, "password_changed_at": t},
        "preferences": {**DEFAULT_PREFERENCES, **(preferences or {})},
        "notifications": {"enabled": False, "types": [], "quiet_hours": None, "followed_route_ids": [],
                          "followed_stop_ids": [], "devices": []},
        "payment_methods": [], "emergency_contacts": list(emergency_contacts or []), "saved_places": [],
        "onboarding": {"walkthrough_completed": False, "paths": [], "dismissed_tips": []},
        "carbon_goal": None, "created_at": t, "updated_at": t,
    }
    try:
        uid = db.users.insert_one(doc).inserted_id
    except DuplicateKeyError:
        raise AccountError("An account with this email already exists. Try signing in or resetting your password.")
    return str(uid), issue_token(db, uid, "verify_email", email)


def issue_token(db, user_id, purpose, email=None):
    """Returns the raw token (send it by email). Older unused tokens for the same purpose are removed."""
    db.auth_tokens.delete_many({"user_id": oid(user_id), "purpose": purpose, "used_at": None})
    raw = secrets.token_urlsafe(32)
    doc = {"user_id": oid(user_id), "purpose": purpose, "token_hash": _hash_token(raw),
           "expires_at": now() + TOKEN_LIFETIME[purpose], "used_at": None, "created_at": now()}
    if email:
        doc["email"] = email
    db.auth_tokens.insert_one(doc)
    return raw


def _consume_token(db, raw, purpose):
    tok = db.auth_tokens.find_one_and_update(
        {"token_hash": _hash_token(raw), "purpose": purpose, "used_at": None, "expires_at": {"$gt": now()}},
        {"$set": {"used_at": now()}})
    if not tok:
        raise AccountError("This link is invalid or has expired. Request a new one.")
    return tok


def verify_email(db, raw_token):
    """Accounts S1 (verify) and S3 (confirm a changed email)."""
    try:
        tok = _consume_token(db, raw_token, "verify_email")
        db.users.update_one({"_id": tok["user_id"]}, {"$set": {"email_verified": True, "updated_at": now()}})
    except AccountError:
        tok = _consume_token(db, raw_token, "change_email")
        try:
            db.users.update_one({"_id": tok["user_id"], "pending_email": tok["email"]},
                                {"$set": {"email": tok["email"], "pending_email": None, "email_verified": True,
                                          "updated_at": now()}})
        except DuplicateKeyError:
            raise AccountError("That email is now used by another account.")
    return str(tok["user_id"])


def resend_verification(db, email):
    """Accounts S1. Returns a new token, or None (don't reveal whether the email exists)."""
    u = db.users.find_one({"email": email.strip().lower(), "email_verified": False})
    return issue_token(db, u["_id"], "verify_email", u["email"]) if u else None


# ------------------------------------------------------------------------------ sign in / out
def sign_in(db, email, password, device=""):
    """Accounts S2. Returns (session_token, user). Locks the account for 15 min after 5 failures."""
    u = db.users.find_one({"email": email.strip().lower()})
    generic = AccountError("Email or password is incorrect.")
    if not u:
        bcrypt.checkpw(b"x", bcrypt.hashpw(b"y", bcrypt.gensalt(4)))  # similar timing either way
        raise generic
    locked = u.get("security", {}).get("locked_until")
    if locked and (locked if locked.tzinfo else locked.replace(tzinfo=now().tzinfo)) > now():
        raise AccountError("Too many failed attempts. Try again in a few minutes or reset your password.")
    if not bcrypt.checkpw(password.encode(), u["password_hash"].encode()):
        fails = u.get("security", {}).get("failed_logins", 0) + 1
        sets = {"security.failed_logins": fails}
        if fails >= MAX_FAILED_LOGINS:
            sets.update({"security.locked_until": now() + LOCKOUT, "security.failed_logins": 0})
        db.users.update_one({"_id": u["_id"]}, {"$set": sets})
        raise generic
    if not u.get("email_verified"):
        raise AccountError("Please verify your email first. We can send the link again.")
    db.users.update_one({"_id": u["_id"]}, {"$set": {"security.failed_logins": 0, "security.locked_until": None}})
    raw = secrets.token_urlsafe(32)
    db.sessions.insert_one({"user_id": u["_id"], "token_hash": _hash_token(raw), "device": device,
                            "created_at": now(), "last_seen_at": now(), "expires_at": now() + SESSION_LIFETIME})
    return raw, public_user(u)


def user_from_session(db, raw_token):
    """Look up the signed-in user from the session token in a cookie / Authorization header."""
    s = db.sessions.find_one_and_update({"token_hash": _hash_token(raw_token), "expires_at": {"$gt": now()}},
                                        {"$set": {"last_seen_at": now()}})
    return db.users.find_one({"_id": s["user_id"]}) if s else None


def sign_out(db, raw_token):
    db.sessions.delete_one({"token_hash": _hash_token(raw_token)})


def request_password_reset(db, email):
    """Accounts S2. Returns a token to email, or None. Always tell the user "if that email exists, we sent a link"."""
    u = db.users.find_one({"email": email.strip().lower()})
    return issue_token(db, u["_id"], "reset_password") if u else None


def reset_password(db, raw_token, new_password):
    problems = password_problems(new_password)
    if problems:
        raise AccountError(" ".join(problems))
    tok = _consume_token(db, raw_token, "reset_password")
    db.users.update_one({"_id": tok["user_id"]}, {"$set": {
        "password_hash": bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode(),
        "security.failed_logins": 0, "security.locked_until": None, "security.password_changed_at": now()}})
    db.sessions.delete_many({"user_id": tok["user_id"]})   # sign out everywhere


# ------------------------------------------------------------------------------ profile
def update_profile(db, user_id, display_name=None, phone=None, email=None):
    """Accounts S3. A new email is held in pending_email until verified; returns that token (or None)."""
    sets = {"updated_at": now()}
    if display_name is not None:
        sets["display_name"] = display_name.strip()
    if phone is not None:
        sets["phone"] = phone
    token = None
    if email:
        email = email.strip().lower()
        if not EMAIL_RE.match(email):
            raise AccountError("Enter a valid email address.")
        if db.users.find_one({"email": email}):
            raise AccountError("That email is already used by another account.")
        sets["pending_email"] = email
    try:
        db.users.update_one({"_id": oid(user_id)}, {"$set": sets})
    except DuplicateKeyError:
        raise AccountError("That email is already used by another account.")
    if email:
        token = issue_token(db, user_id, "change_email", email)
    return token


def delete_account(db, user_id):
    """Accounts S3: deletes the user and everything they own (trips, orders, tickets, contacts...)."""
    uid = oid(user_id)
    counts = {name: db[name].delete_many({"user_id": uid}).deleted_count for name in USER_OWNED}
    counts["users"] = db.users.delete_one({"_id": uid}).deleted_count
    return counts


# ------------------------------------------------------------------------------ settings
PREFERENCE_KEYS = set(DEFAULT_PREFERENCES)


def update_preferences(db, user_id, **prefs):
    """Themes S1, S2, S4, S5; Weather S1 (temperature_unit); Carbon S3 (comparison_vehicle)."""
    bad = set(prefs) - PREFERENCE_KEYS
    if bad:
        raise AccountError(f"Unknown setting(s): {', '.join(sorted(bad))}")
    db.users.update_one({"_id": oid(user_id)},
                        {"$set": {**{f"preferences.{k}": v for k, v in prefs.items()}, "updated_at": now()}})


def reset_preferences(db, user_id):
    """Themes S5: reset to defaults."""
    db.users.update_one({"_id": oid(user_id)}, {"$set": {"preferences": dict(DEFAULT_PREFERENCES), "updated_at": now()}})


def update_notification_settings(db, user_id, **settings):
    """Real-Time S4: enabled, types, quiet_hours {"start": "22:00", "end": "07:00"},
    followed_route_ids, followed_stop_ids."""
    allowed = {"enabled", "types", "quiet_hours", "followed_route_ids", "followed_stop_ids"}
    sets = {f"notifications.{k}": v for k, v in settings.items() if k in allowed}
    db.users.update_one({"_id": oid(user_id)}, {"$set": {**sets, "updated_at": now()}})


def add_push_device(db, user_id, token, platform):
    db.users.update_one({"_id": oid(user_id)}, {"$pull": {"notifications.devices": {"token": token}}})
    db.users.update_one({"_id": oid(user_id)}, {"$push": {"notifications.devices": {
        "token": token, "platform": platform, "added_at": now()}}})


# ------------------------------------------------------------------------------ payment methods (simulated)
def add_payment_method(db, user_id, card_number, exp_month, exp_year, label="", make_default=False):
    """Accounts S4. Rejects anything that isn't a known test card. Stores brand + last 4 only."""
    digits = re.sub(r"\D", "", card_number)
    brand = TEST_CARDS.get(digits)
    if not brand:
        raise AccountError("Only test card numbers are accepted. This app never charges real money.")
    pm = {"id": "pm_" + secrets.token_hex(6), "brand": brand, "last4": digits[-4:], "exp_month": int(exp_month),
          "exp_year": int(exp_year), "is_default": False, "is_test": True, "label": label or f"Test {brand.title()}"}
    u = db.users.find_one({"_id": oid(user_id)}, {"payment_methods": 1})
    first = not u.get("payment_methods")
    db.users.update_one({"_id": oid(user_id)}, {"$push": {"payment_methods": pm}})
    if make_default or first:
        set_default_payment_method(db, user_id, pm["id"])
    return pm["id"]


def _set_only_flag(db, user_id, field, flag, item_id):
    """Set `flag` True on the one array item with this id and False on the rest."""
    u = db.users.find_one({"_id": oid(user_id)}, {field: 1}) or {}
    items = [{**i, flag: i["id"] == item_id} for i in u.get(field, [])]
    db.users.update_one({"_id": oid(user_id)}, {"$set": {field: items, "updated_at": now()}})


def set_default_payment_method(db, user_id, method_id):
    _set_only_flag(db, user_id, "payment_methods", "is_default", method_id)


def remove_payment_method(db, user_id, method_id, replacement_id=None):
    """Accounts S4: if an active pass was bought with this card, ask for a replacement first.
    Returns {"needs_replacement": True} in that case."""
    in_use = db.orders.find_one({"user_id": oid(user_id), "payment.method_id": method_id, "status": "succeeded",
                                 "_id": {"$in": db.tickets.distinct("order_id", {"user_id": oid(user_id),
                                                                                 "status": "active"})}})
    if in_use and not replacement_id:
        return {"needs_replacement": True}
    db.users.update_one({"_id": oid(user_id)}, {"$pull": {"payment_methods": {"id": method_id}}})
    if replacement_id:
        set_default_payment_method(db, user_id, replacement_id)
    return {"removed": True}


# ------------------------------------------------------------------------------ emergency contacts (Emergency S2)
def add_emergency_contact(db, user_id, name, phone, relationship="", is_primary=False):
    c = {"id": "ec_" + secrets.token_hex(4), "name": name, "phone": phone, "relationship": relationship,
         "is_primary": False}
    db.users.update_one({"_id": oid(user_id)}, {"$push": {"emergency_contacts": c}})
    if is_primary:
        set_primary_contact(db, user_id, c["id"])
    return c["id"]


def update_emergency_contact(db, user_id, contact_id, **fields):
    sets = {f"emergency_contacts.$.{k}": v for k, v in fields.items() if k in {"name", "phone", "relationship"}}
    db.users.update_one({"_id": oid(user_id), "emergency_contacts.id": contact_id}, {"$set": sets})


def set_primary_contact(db, user_id, contact_id):
    _set_only_flag(db, user_id, "emergency_contacts", "is_primary", contact_id)


def delete_emergency_contact(db, user_id, contact_id):
    """Call only after the user confirms."""
    db.users.update_one({"_id": oid(user_id)}, {"$pull": {"emergency_contacts": {"id": contact_id}}})


def emergency_contacts(db, user_id):
    """Primary first."""
    u = db.users.find_one({"_id": oid(user_id)}, {"emergency_contacts": 1}) or {}
    return sorted(u.get("emergency_contacts", []), key=lambda c: not c.get("is_primary"))


# ------------------------------------------------------------------------------ saved places (Local Businesses S4)
def save_place(db, user_id, place):
    """place = {"name", "location", "business_id"?, "address"?}. No duplicates by business_id/name."""
    key = {"business_id": oid(place["business_id"])} if place.get("business_id") else {"name": place["name"]}
    if "business_id" in place:
        place = {**place, "business_id": oid(place["business_id"])}
    db.users.update_one({"_id": oid(user_id)}, {"$pull": {"saved_places": key}})
    db.users.update_one({"_id": oid(user_id)}, {"$push": {"saved_places": place}})


def remove_place(db, user_id, business_id=None, name=None):
    key = {"business_id": oid(business_id)} if business_id else {"name": name}
    db.users.update_one({"_id": oid(user_id)}, {"$pull": {"saved_places": key}})


# ------------------------------------------------------------------------------ onboarding / carbon goal
def update_onboarding(db, user_id, **fields):
    """Onboarding S1, S3: walkthrough_completed, accessibility_prompt_seen, paths, dismissed_tips."""
    allowed = {"walkthrough_completed", "accessibility_prompt_seen", "paths", "dismissed_tips"}
    sets = {f"onboarding.{k}": v for k, v in fields.items() if k in allowed}
    if fields.get("walkthrough_completed"):
        sets["onboarding.walkthrough_completed_at"] = now()
    db.users.update_one({"_id": oid(user_id)}, {"$set": sets})


def set_carbon_goal(db, user_id, kind, target, period="month"):
    """Carbon S4. kind = "co2_avoided_kg" | "car_free_trips". Pass kind=None to remove the goal."""
    goal = None if kind is None else {"kind": kind, "target": target, "period": period,
                                      "starts_at": now(), "achieved_at": None}
    db.users.update_one({"_id": oid(user_id)}, {"$set": {"carbon_goal": goal}})
