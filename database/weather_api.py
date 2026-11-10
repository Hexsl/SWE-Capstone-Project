"""Live weather for TransitHub NYC.

Forecast data comes from Open-Meteo (https://open-meteo.com), which needs no API key.
Severe weather alerts come from the US National Weather Service (api.weather.gov), also keyless.
Only the standard library is used, so there is nothing extra to install.

fetch_weather() returns the same shape that queries.save_weather() stores:
    {"current": {...}, "hourly": [...], "daily": [...], "alerts": [...]}
Temperatures are Celsius and wind is km/h; the app converts them for display.
"""
import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

SOURCE = "open-meteo"
TIMEOUT_SECONDS = 6
USER_AGENT = "TransitHubNYC/1.0 (student capstone project)"   # api.weather.gov requires one

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
ALERTS_URL = "https://api.weather.gov/alerts/active"

# WMO weather codes used by Open-Meteo -> plain words (Weather S1: conditions in words, not just an icon)
WMO = {
    0: "Clear", 1: "Mostly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Freezing fog",
    51: "Light drizzle", 53: "Drizzle", 55: "Heavy drizzle", 56: "Freezing drizzle", 57: "Heavy freezing drizzle",
    61: "Light rain", 63: "Rain", 65: "Heavy rain", 66: "Freezing rain", 67: "Heavy freezing rain",
    71: "Light snow", 73: "Snow", 75: "Heavy snow", 77: "Snow grains",
    80: "Light showers", 81: "Showers", 82: "Heavy showers", 85: "Snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Severe thunderstorm with hail",
}

COMPASS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]


class WeatherError(Exception):
    """The weather source could not be reached or returned something unusable."""


def describe(code):
    return WMO.get(int(code), "Unknown") if code is not None else "Unknown"


def compass(degrees):
    if degrees is None:
        return None
    return COMPASS[int((degrees % 360) / 22.5 + 0.5) % 16]


def _get_json(url, params=None):
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as res:
            return json.loads(res.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
        raise WeatherError(str(exc)) from exc


def _parse_time(text, tz):
    """Open-Meteo gives local times without an offset, e.g. '2026-11-09T22:00'."""
    return datetime.fromisoformat(text).replace(tzinfo=tz)


def _parse_iso(text):
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def parse_forecast(data):
    """Turn an Open-Meteo response into our stored shape. Raises WeatherError if it is incomplete."""
    try:
        tz = timezone(timedelta(seconds=data.get("utc_offset_seconds", 0)))
        cur = data["current"]
        current = {
            "temp_c": cur["temperature_2m"],
            "feels_like_c": cur["apparent_temperature"],
            "conditions": describe(cur["weather_code"]),
            "precip_mm": cur.get("precipitation") or 0,
            "wind_kph": cur["wind_speed_10m"],
            "wind_dir": compass(cur.get("wind_direction_10m")),
        }
        hourly_in = data["hourly"]
        hourly = []
        for i, t in enumerate(hourly_in["time"]):
            item = {"time": _parse_time(t, tz), "temp_c": hourly_in["temperature_2m"][i],
                    "conditions": describe(hourly_in["weather_code"][i])}
            chance = hourly_in["precipitation_probability"][i]
            if chance is not None:
                item["precip_chance"] = chance
            hourly.append(item)
        daily_in = data["daily"]
        daily = []
        for i, d in enumerate(daily_in["time"]):
            item = {"date": _parse_time(d + "T00:00", tz), "high_c": daily_in["temperature_2m_max"][i],
                    "low_c": daily_in["temperature_2m_min"][i], "conditions": describe(daily_in["weather_code"][i])}
            chance = daily_in["precipitation_probability_max"][i]
            if chance is not None:
                item["precip_chance"] = chance
            daily.append(item)
        # "precip_chance" for right now: the current hour's chance of rain
        if hourly and "precip_chance" in hourly[0]:
            current["precip_chance"] = hourly[0]["precip_chance"]
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise WeatherError("Unexpected response from the weather service") from exc
    return {"current": current, "hourly": hourly[:48], "daily": daily, "alerts": []}


def fetch_alerts(lat, lon):
    """Active NWS alerts for a point. Best effort: any failure returns an empty list, because a missing
    alert feed should not stop the forecast from showing."""
    try:
        data = _get_json(ALERTS_URL, {"point": f"{lat:.4f},{lon:.4f}"})
    except WeatherError:
        return []
    alerts = []
    for feature in data.get("features", []):
        p = feature.get("properties") or {}
        if not p.get("event"):
            continue
        alert = {"event": p["event"], "severity": p.get("severity") or "Unknown",
                 "headline": p.get("headline") or p["event"]}
        starts = _parse_iso(p.get("onset") or p.get("effective"))
        ends = _parse_iso(p.get("ends") or p.get("expires"))
        if starts:
            alert["starts"] = starts
        if ends:
            alert["ends"] = ends
        alerts.append(alert)
    return alerts


def fetch_weather(lat, lon):
    data = _get_json(FORECAST_URL, {
        "latitude": f"{lat:.4f}", "longitude": f"{lon:.4f}",
        "current": "temperature_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,wind_direction_10m",
        "hourly": "temperature_2m,precipitation_probability,weather_code",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "forecast_hours": 48, "forecast_days": 7, "timezone": "auto",
    })
    report = parse_forecast(data)
    report["alerts"] = fetch_alerts(lat, lon)
    return report


def trip_advice(report):
    """Weather S3: one-line tips for riders, based on the report."""
    tips = []
    cur = report.get("current", {})
    chance = max([cur.get("precip_chance") or 0] + [h.get("precip_chance") or 0 for h in report.get("hourly", [])[:6]])
    cond = (cur.get("conditions") or "").lower()
    if chance >= 50 or any(w in cond for w in ("rain", "drizzle", "shower", "thunder")):
        tips.append("Bring an umbrella. Consider a covered route or waiting inside a station.")
    if "snow" in cond:
        tips.append("Snow can slow buses and trains. Leave extra time.")
    feels = cur.get("feels_like_c")
    if feels is not None and feels >= 32:
        tips.append("Extreme heat. Drink water and wait in air-conditioned spaces when you can.")
    if feels is not None and feels <= -7:
        tips.append("Very cold. Dress warmly and limit time waiting outdoors.")
    if (cur.get("wind_kph") or 0) >= 45:
        tips.append("Strong wind. Be careful on outdoor platforms and bridges.")
    return tips
