from fastapi import APIRouter, Query
from app.services.forecast_service import get_forecast_data

router = APIRouter()

@router.get("/forecast")
async def get_forecast(location: str = Query(..., description="City name or ZIP code")):
    forecast = await get_forecast_data(location)
    return forecast
