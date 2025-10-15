from fastapi import APIRouter, Query
from app.services.weather_service import get_current_weather, get_forecast
from app.utils.geolocation import get_location_from_ip

router = APIRouter()

@router.get("/weather")
def read_weather(location: str = Query(None, description="City name or ZIP code")):
    """
    Fetch current weather data for a given location.
    If no location is provided, attempt to determine via IP.
    """
    if not location:
        location = get_location_from_ip()
    return get_current_weather(location)


@router.get("/forecast")
def read_forecast(location: str = Query(None, description="City name or ZIP code")):
    """
    Fetch 5-day weather forecast for a given location.
    If no location is provided, attempt to determine via IP.
    """
    if not location:
        location = get_location_from_ip()
    return get_forecast(location)
