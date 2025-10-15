from fastapi import APIRouter, Query
from app.services.forecast_service import get_forecast

router = APIRouter()

@router.get("/forecast")
def forecast(location: str = Query(..., description="City name or ZIP code")):
    return get_forecast(location)
