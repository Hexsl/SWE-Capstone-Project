"""Weather parsing and advice. No network and no database needed."""
from datetime import timezone

import pytest

from database import weather_api as w

HOURS = [f"2026-11-09T{h:02d}:00" for h in range(24)]


def forecast(code=61, feels=6.1, wind=18.0, chance=70):
    """A response in Open-Meteo's shape, in New York time (UTC-5)."""
    return {
        "utc_offset_seconds": -18000,
        "current": {"temperature_2m": 8.5, "apparent_temperature": feels, "precipitation": 0.2,
                    "weather_code": code, "wind_speed_10m": wind, "wind_direction_10m": 300},
        "hourly": {"time": HOURS, "temperature_2m": [8] * 24, "weather_code": [3] * 24,
                   "precipitation_probability": [chance] + [None] * 23},
        "daily": {"time": ["2026-11-09", "2026-11-10"], "weather_code": [61, 2], "temperature_2m_max": [10, 12],
                  "temperature_2m_min": [4, 5], "precipitation_probability_max": [80, None]},
    }


def test_current_conditions_are_described_in_words():
    cur = w.parse_forecast(forecast())["current"]
    assert cur["conditions"] == "Light rain"
    assert cur["temp_c"] == 8.5 and cur["feels_like_c"] == 6.1
    assert cur["wind_dir"] == "WNW"           # 300 degrees
    assert cur["precip_chance"] == 70


def test_times_keep_the_new_york_offset():
    report = w.parse_forecast(forecast())
    assert report["hourly"][0]["time"].utcoffset().total_seconds() == -18000
    assert report["hourly"][0]["time"].astimezone(timezone.utc).hour == 5


def test_missing_rain_chance_is_left_out_not_zero():
    daily = w.parse_forecast(forecast())["daily"]
    assert daily[0]["precip_chance"] == 80
    assert "precip_chance" not in daily[1]


def test_unknown_weather_code_does_not_crash():
    assert w.describe(1234) == "Unknown"


def test_incomplete_response_raises_weather_error():
    with pytest.raises(w.WeatherError):
        w.parse_forecast({"current": {}})


def test_rain_gets_umbrella_advice_and_clear_weather_gets_none():
    assert any("umbrella" in t for t in w.trip_advice(w.parse_forecast(forecast())))
    dry = w.parse_forecast(forecast(code=0, chance=0))
    assert w.trip_advice(dry) == []


def test_extreme_heat_and_wind_get_warnings():
    report = w.parse_forecast(forecast(code=0, feels=35, wind=60, chance=0))
    advice = " ".join(w.trip_advice(report))
    assert "heat" in advice and "wind" in advice
