from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from database import accounts, queries
from database.db import get_db, ping


@api_view(["GET"])
def health(request):
    """GET /api/health/ - confirms Django is up and MongoDB is reachable."""
    try:
        ping()
    except Exception:
        return Response({"status": "degraded", "mongodb": "unreachable"}, status=503)
    return Response({"status": "ok", "mongodb": "ok"})


@api_view(["POST"])
def signup(request):
    """POST /api/signup/  {name, email, password, confirm}"""
    data = request.data
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""
    if not name:
        return Response({"error": "Enter your full name."}, status=400)
    if "confirm" in data and password != data.get("confirm"):
        return Response({"error": "Passwords do not match."}, status=400)
    try:
        db = get_db()
        _, verify_token = accounts.create_user(db, email, password, name)
        # DEMO ONLY: email sending isn't built, so we "click" the verification link for the user.
        accounts.verify_email(db, verify_token)
    except accounts.AccountError as exc:
        return Response({"error": str(exc)}, status=400)
    return Response({"ok": True}, status=201)


@api_view(["POST"])
def login(request):
    """POST /api/login/  {email, password}  ->  {token, user}"""
    email = (request.data.get("email") or "").strip()
    password = request.data.get("password") or ""
    try:
        token, user = accounts.sign_in(get_db(), email, password, device="app")
    except accounts.AccountError as exc:
        return Response({"error": str(exc)}, status=400)
    return Response({"token": token,
                        "user": {"display_name": user.get("display_name"), "email": user.get("email"),
                                 "role": user.get("role")}})


@api_view(["POST"])
def logout(request):
    """POST /api/logout/  (send the Bearer token)"""
    if request.auth:
        accounts.sign_out(get_db(), request.auth)
    return Response({"ok": True})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    """GET /api/me/  - who is signed in"""
    doc = request.user.doc
    return Response({"display_name": doc.get("display_name"), "email": doc.get("email")})


@api_view(["GET"])
def nearby_stops(request):
    """GET /api/stops/nearby/?lat=&lon=  - defaults to Times Square, like the Figma."""
    try:
        lat = float(request.query_params.get("lat", 40.7553))
        lon = float(request.query_params.get("lon", -73.9871))
    except ValueError:
        return Response({"error": "lat and lon must be numbers."}, status=400)
    stops = queries.nearby_stops(get_db(), lat, lon, max_meters=6000)
    return Response([
        {"stop_id": s.get("stop_id"), "name": s.get("name"), "mode": s.get("mode"),
         "route_ids": s.get("route_ids", []), "walk_minutes": s.get("walk_minutes"),
         "distance_m": round(s.get("distance_m", 0))}
        for s in stops
    ])


@api_view(["GET"])
def map_layer(request):
    """GET /api/map/?agency=LIRR  - all stations and branch lines for the map."""
    agency = request.query_params.get("agency", "LIRR")
    data = queries.map_layer(get_db(), agency)
    return Response({
        "stops": [{"stop_id": s["stop_id"], "name": s["name"],
                   "lon": s["location"]["coordinates"][0], "lat": s["location"]["coordinates"][1],
                   "route_ids": s.get("route_ids", []), "accessible": s.get("wheelchair_accessible", False)}
                  for s in data["stops"]],
        "routes": [{"route_id": r["route_id"], "name": r.get("long_name") or r["short_name"],
                    "color": r.get("color", "#4D5357"), "text_color": r.get("text_color", "#FFFFFF"),
                    "lines": (r.get("shape") or {}).get("coordinates", [])}
                   for r in data["routes"]],
    })


@api_view(["GET"])
def fares(request):
    """GET /api/fares/  - the tickets people can buy."""
    items = queries.fare_products(get_db(), include_reduced=False)
    return Response([
        {"code": f["code"], "name": f["name"], "price_usd": f["price_usd"],
         "description": f.get("description", "")}
        for f in items
    ])


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def purchase(request):
    """POST /api/purchase/  {fare_code, idempotency_key}  - simulated payment, test card only."""
    fare_code = request.data.get("fare_code")
    key = request.data.get("idempotency_key")
    if not fare_code or not key:
        return Response({"error": "Choose a ticket first."}, status=400)
    db = get_db()
    user_id = request.user.id
    methods = request.user.doc.get("payment_methods") or []
    try:
        if not methods:
            # DEMO: give the account the Stripe 4242 test card so the purchase can go through
            method_id = accounts.add_payment_method(db, user_id, "4242424242424242", 12, 2030, label="Demo Card")
        else:
            method_id = next((m["id"] for m in methods if m.get("is_default")), methods[0]["id"])
        order = queries.purchase_tickets(db, user_id, [{"fare_code": fare_code, "quantity": 1}], method_id, key)
    except ValueError as exc:   # includes AccountError
        return Response({"error": str(exc)}, status=400)
    if order.get("status") != "succeeded":
        return Response({"error": order.get("failure_reason") or "Payment failed."}, status=400)
    return Response({"receipt_number": order["receipt_number"], "total_usd": order["total_usd"],
                     "ticket": order["items"][0]["name"], "created_at": order["created_at"]})