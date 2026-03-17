import os
from datetime import datetime, timezone as dt_timezone
from typing import Any

import requests
from django.utils import timezone

OPENWEATHER_GEOCODING_URL = "http://api.openweathermap.org/geo/1.0/direct"
OPENWEATHER_CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
OPENWEATHER_FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"


def _safe_get(dictionary: dict[str, Any], *keys: str, default: Any = None) -> Any:
    current: Any = dictionary
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def build_local_summary(city: str, current: dict[str, Any], forecast: list[dict[str, Any]]) -> str:
    temp = current.get("temperature")
    condition = current.get("condition")
    humidity = current.get("humidity")
    wind = current.get("wind_speed")
    overview = (
        f"In {city}, it is currently {temp}°C with {condition.lower()} conditions. "
        f"Humidity sits at {humidity}% and wind speed is {wind} m/s."
    )
    if forecast:
        warmest = max(forecast, key=lambda day: day["temp_max"])
        coolest = min(forecast, key=lambda day: day["temp_min"])
        trend = (
            f" Over the next days, expect the warmest period on {warmest['date']} "
            f"({warmest['temp_max']}°C) and the coolest on {coolest['date']} ({coolest['temp_min']}°C)."
        )
    else:
        trend = ""
    return overview + trend


def generate_ai_summary(city: str, current: dict[str, Any], forecast: list[dict[str, Any]]) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return build_local_summary(city, current, forecast)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        prompt = {
            "city": city,
            "current": current,
            "forecast": forecast,
            "generated_at": timezone.now().isoformat(),
        }
        completion = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0.5,
            messages=[
                {
                    "role": "system",
                    "content": "You are a weather assistant. Keep responses concise, practical, and human-friendly.",
                },
                {
                    "role": "user",
                    "content": (
                        "Create a 3-4 sentence weather summary with outfit/activity advice and mention one risk "
                        "if relevant. Data: "
                        f"{prompt}"
                    ),
                },
            ],
        )
        return completion.choices[0].message.content.strip()
    except Exception:
        return build_local_summary(city, current, forecast)


def fetch_weather(city: str) -> dict[str, Any]:
    weather_api_key = os.getenv("OPENWEATHER_API_KEY")
    if not weather_api_key:
        raise ValueError("OPENWEATHER_API_KEY is not configured.")

    geocode_response = requests.get(
        OPENWEATHER_GEOCODING_URL,
        params={"q": city, "limit": 1, "appid": weather_api_key},
        timeout=10,
    )
    geocode_response.raise_for_status()
    locations = geocode_response.json()

    if not locations:
        raise ValueError("City not found. Please try a different city.")

    location = locations[0]
    lat, lon = location["lat"], location["lon"]
    canonical_city = location.get("name", city)
    country = location.get("country", "")

    current_response = requests.get(
        OPENWEATHER_CURRENT_URL,
        params={"lat": lat, "lon": lon, "appid": weather_api_key, "units": "metric"},
        timeout=10,
    )
    current_response.raise_for_status()
    current_data = current_response.json()

    forecast_response = requests.get(
        OPENWEATHER_FORECAST_URL,
        params={"lat": lat, "lon": lon, "appid": weather_api_key, "units": "metric"},
        timeout=10,
    )
    forecast_response.raise_for_status()
    forecast_data = forecast_response.json()

    current = {
        "temperature": round(_safe_get(current_data, "main", "temp", default=0), 1),
        "humidity": _safe_get(current_data, "main", "humidity", default=0),
        "wind_speed": round(_safe_get(current_data, "wind", "speed", default=0), 1),
        "condition": _safe_get(current_data, "weather", default=[{"main": "Unknown"}])[0]["main"],
        "description": _safe_get(current_data, "weather", default=[{"description": "n/a"}])[0]["description"],
    }

    grouped_forecast: dict[str, list[dict[str, Any]]] = {}
    for item in forecast_data.get("list", []):
        dt_txt = item.get("dt_txt")
        if not dt_txt:
            continue
        day = dt_txt.split(" ")[0]
        grouped_forecast.setdefault(day, []).append(item)

    next_five_days = []
    for day, entries in list(grouped_forecast.items())[:5]:
        min_temp = min(entry["main"]["temp_min"] for entry in entries)
        max_temp = max(entry["main"]["temp_max"] for entry in entries)
        midday = min(
            entries,
            key=lambda entry: abs(
                datetime.fromtimestamp(entry["dt"]).replace(tzinfo=dt_timezone.utc).hour - 12
            ),
        )
        next_five_days.append(
            {
                "date": day,
                "temp_min": round(min_temp, 1),
                "temp_max": round(max_temp, 1),
                "condition": midday["weather"][0]["main"],
            }
        )

    ai_summary = generate_ai_summary(canonical_city, current, next_five_days)

    return {
        "city": canonical_city,
        "country": country,
        "current": current,
        "forecast": next_five_days,
        "ai_summary": ai_summary,
    }
