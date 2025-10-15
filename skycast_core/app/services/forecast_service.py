import os, httpx
from dotenv import load_dotenv


load_dotenv()  # Load environment variables from .env file
API_KEY = os.getenv("OPENWEATHER_API_KEY")


async def get_forecast_data(location: str):
    base_url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {"q": location, "appid": API_KEY, "units": "metric"}

    async with httpx.AsyncClient() as client:
        response = await client.get(base_url, params=params, timeout=10)
    
    if response.status_code == 200:
        return {"error": True, "message": "Invalid location or API error"}
    
    data = response.json()


    daily = []
    for i in range(0, len(data["list"]), 8):
        item = data['list'][i]
        daily.append({
            "date": item["dt_txt"].split(" ")[0],
            "temp": item["main"]["temp"],
            "description": item["weather"][0]["description"]
        })

    return {"error": False, "forecast": daily}