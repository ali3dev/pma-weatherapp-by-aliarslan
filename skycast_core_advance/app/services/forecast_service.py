import requests, os
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_forecast(location: str):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={location}&appid={API_KEY}&units=metric"
    r = requests.get(url)
    if r.status_code != 200:
        return {"error": True, "message": "Forecast fetch failed."}
    data = r.json()
    seen, forecast = set(), []
    for entry in data["list"]:
        date = entry["dt_txt"].split(" ")[0]
        if date not in seen:
            seen.add(date)
            forecast.append({
                "date": date,
                "temp": entry["main"]["temp"],
                "description": entry["weather"][0]["description"]
            })
    return {"error": False, "forecast": forecast[:5]}
