import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")


def build_url(base_url: str, location: str):
    """
    Detects input type (city, ZIP, or coordinates) and builds the correct OpenWeatherMap API URL.
    """
    # GPS coordinates check (e.g. "31.5497,74.3436")
    if "," in location:
        parts = [p.strip() for p in location.split(",")]
        if len(parts) == 2 and all(x.replace('.', '', 1).replace('-', '', 1).isdigit() for x in parts):
            lat, lon = map(float, parts)
            return f"{base_url}?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"

    # ZIP code with country (e.g. "94040,US")
    if location.replace(",", "").replace("-", "").isdigit() or "," in location:
        return f"{base_url}?zip={location}&appid={API_KEY}&units=metric"

    # Default: treat as city or landmark
    return f"{base_url}?q={location}&appid={API_KEY}&units=metric"


def get_current_weather(location: str):
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    url = build_url(base_url, location)
    response = requests.get(url)

    if response.status_code != 200:
        return {"error": True, "message": "Failed to fetch current weather"}

    return {"error": False, "data": response.json()}


def get_forecast(location: str):
    base_url = "https://api.openweathermap.org/data/2.5/forecast"
    url = build_url(base_url, location)
    response = requests.get(url)

    if response.status_code != 200:
        return {"error": True, "message": "Failed to fetch forecast"}

    data = response.json()
    forecast = []
    seen_dates = set()

    for entry in data["list"]:
        date = entry["dt_txt"].split(" ")[0]
        if date not in seen_dates:
            seen_dates.add(date)
            forecast.append({
                "date": date,
                "temp": entry["main"]["temp"],
                "description": entry["weather"][0]["description"]
            })

    return {"error": False, "forecast": forecast[:5]}
