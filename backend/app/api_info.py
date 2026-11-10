from datetime import timedelta

from rest_framework.decorators import api_view
from rest_framework.response import Response

from database import queries, weather_api
from database.db import get_db

# Times Square. Used when the app does not send a location.
DEFAULT_LAT, DEFAULT_LON = 40.7580, -73.9855
CACHE_MINUTES = 30


@api_view(["GET"])
def emergency(request):
    """GET /api/emergency/  - public help numbers (911, police, MTA Police, ...), in display order."""
    data = queries.emergency_info(get_db())
    return Response({"items": [{"key": i.get("key"), "name": i.get("name"), "category": i.get("category"),
                                "phone": i.get("phone"), "sms": i.get("sms"), "url": i.get("url"),
                                "when_to_use": i.get("when_to_use", "")} for i in data["items"]],
                     "updated_at": data["updated_at"]})


def _fresh(cached):
    """True if the cache holds a live report that is under CACHE_MINUTES old. The seed's sample report
    has a different source, so it is never served as real weather."""
    if not cached or cached.get("source") != weather_api.SOURCE or not cached.get("fetched_at"):
        return False
    fetched = cached["fetched_at"]
    if fetched.tzinfo is None:
        fetched = fetched.replace(tzinfo=queries.now().tzinfo)
    return queries.now() - fetched < timedelta(minutes=CACHE_MINUTES)


def _public(report, stale=False):
    return {"current": report.get("current", {}), "hourly": report.get("hourly", []),
            "daily": report.get("daily", []), "alerts": report.get("alerts", []),
            "advice": weather_api.trip_advice(report), "updated_at": report.get("fetched_at"),
            "source": report.get("source"), "stale": stale}


@api_view(["GET"])
def weather(request):
    """GET /api/weather/?lat=40.76&lon=-73.99  - live weather, cached for 30 minutes per area.

    If the weather source is down, the last saved report is returned with stale=true."""
    try:
        lat = float(request.query_params.get("lat", DEFAULT_LAT))
        lon = float(request.query_params.get("lon", DEFAULT_LON))
    except ValueError:
        return Response({"error": "lat and lon must be numbers."}, status=400)
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return Response({"error": "That location is out of range."}, status=400)

    db = get_db()
    cached = queries.cached_weather(db, lat, lon)
    if _fresh(cached):
        return Response(_public(cached))
    try:
        report = weather_api.fetch_weather(lat, lon)
    except weather_api.WeatherError:
        if cached and cached.get("source") == weather_api.SOURCE:
            return Response(_public(cached, stale=True))
        return Response({"error": "Weather is unavailable right now. Please try again."}, status=503)
    queries.save_weather(db, lat, lon, report["current"], report["hourly"], report["daily"],
                         report["alerts"], source=weather_api.SOURCE)
    return Response(_public(queries.cached_weather(db, lat, lon)))
