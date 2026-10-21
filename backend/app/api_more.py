import uuid
from datetime import timedelta

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from database import queries
from database.db import get_db


def _is_admin(request):
    return request.user.doc.get("role") == "admin"


def _brief_alert(a):
    periods = a.get("active_periods") or [{}]
    return {"alert_id": a.get("alert_id"), "header": a.get("header"), "description": a.get("description", ""),
            "effect": a.get("effect"), "severity": a.get("severity"), "is_planned": a.get("is_planned", False),
            "route_ids": a.get("route_ids", []), "start": periods[0].get("start")}


@api_view(["GET"])
def alerts(request):
    """GET /api/alerts/  - current disruptions and planned work."""
    data = queries.alerts_list(get_db())
    return Response({"current": [_brief_alert(a) for a in data["current"]],
                     "planned": [_brief_alert(a) for a in data["planned"]]})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def trips(request):
    """GET /api/trips/?mode=subway  - the signed-in user's past trips, newest first."""
    mode = request.query_params.get("mode") or None
    out = []
    for t in queries.trip_history(get_db(), request.user.id, mode=mode, limit=30):
        legs = t.get("legs") or []
        main = next((l for l in legs if l.get("mode") not in ("walk", "bike")), legs[0] if legs else {})
        out.append({"id": t.get("_id"),
                    "origin": (t.get("origin") or {}).get("name"),
                    "destination": (t.get("destination") or {}).get("name"),
                    "mode": main.get("mode"),
                    "line": main.get("line_name") or main.get("route_id"),
                    "depart_at": t.get("depart_at")})
    return Response(out)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def report_issue(request):
    """POST /api/reports/  {kind, subject, message}  - a rider reports a problem."""
    message = (request.data.get("message") or "").strip()
    if not message:
        return Response({"error": "Describe the problem first."}, status=400)
    kind = request.data.get("kind") or "problem"
    subject = (request.data.get("subject") or "").strip()
    rid = queries.create_support_request(get_db(), request.user.id, kind, message, subject=subject)
    return Response({"id": rid}, status=201)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_summary(request):
    """GET /api/admin/summary/  - numbers for the admin dashboard (admins only)."""
    if not _is_admin(request):
        return Response({"error": "Admins only."}, status=403)
    db = get_db()
    return Response({"stops": db.stops.count_documents({}),
                     "active_alerts": len(queries.active_alerts(db)),
                     "reports_open": db.support_requests.count_documents({"status": "open"})})


REPORT_STATUS = {"received": "open", "in_progress": "in_progress"}


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_reports(request):
    """GET /api/admin/reports/?status=received|in_progress  (admins only)."""
    if not _is_admin(request):
        return Response({"error": "Admins only."}, status=403)
    status = REPORT_STATUS.get(request.query_params.get("status"))
    q = {"status": status} if status else {}
    rows = get_db().support_requests.find(q).sort("created_at", -1).limit(50)
    return Response([{"id": str(r["_id"]), "kind": r.get("kind"), "subject": r.get("subject") or "",
                      "message": r.get("message"), "status": r.get("status"),
                      "created_at": r.get("created_at")} for r in rows])


ALERT_TYPES = {  # label shown in the app -> (effect, is_planned)
    "Service Change": ("reroute", False),
    "Delay": ("delay", False),
    "Planned Work": ("planned_work", True),
    "Elevator Outage": ("elevator_outage", False),
}


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def admin_create_alert(request):
    """POST /api/admin/alerts/  {type, days, start_time, end_time}  (admins only)."""
    if not _is_admin(request):
        return Response({"error": "Admins only."}, status=403)
    kind = request.data.get("type")
    if kind not in ALERT_TYPES:
        return Response({"error": "Choose a type of alert."}, status=400)
    days = request.data.get("days") or []
    start_t = request.data.get("start_time") or "06:00"
    end_t = request.data.get("end_time") or "17:00"
    effect, planned = ALERT_TYPES[kind]
    t = queries.now()
    # The database has no repeat-schedule field yet, so the days and times go in the description
    # and the alert is active for the next 7 days.
    get_db().service_alerts.insert_one({
        "alert_id": "admin-" + uuid.uuid4().hex[:8],
        "header": kind + " on all lines",
        "description": "Applies " + (", ".join(days) if days else "every day") + " from " + start_t + " to " + end_t + ".",
        "effect": effect, "severity": "warning", "is_planned": planned,
        "route_ids": [], "stop_ids": [],
        "active_periods": [{"start": t, "end": t + timedelta(days=7)}],
        "source": "admin", "updated_at": t,
    })
    return Response({"ok": True}, status=201)