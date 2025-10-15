from fastapi import APIRouter, Query
from app.services import weather_service, forecast_service

router = APIRouter()

@router.get("/weather")
def read_weather(location: str = Query(...)):
    return weather_service.get_current_weather(location)

@router.get("/records")
def get_records():
    return weather_service.get_all_records()

@router.put("/update/{record_id}")
def update_weather(record_id: int, desc: str):
    return weather_service.update_record(record_id, desc)

@router.delete("/delete/{record_id}")
def delete_weather(record_id: int):
    return weather_service.delete_record(record_id)

@router.get("/forecast")
def read_forecast(location: str = Query(...)):
    return forecast_service.get_forecast(location)


@router.get("/create_range")
@router.post("/create_range")
def create_range(location: str = Query(...), start_date: str = Query(...), end_date: str = Query(...)):
    return weather_service.create_range(location, start_date, end_date)


@router.post("/delete_batch")
def delete_batch(ids: str = Query(...)):
    """Delete multiple records. Provide comma-separated IDs in the `ids` query param, e.g. ids=1,2,3"""
    try:
        ids_list = [int(x.strip()) for x in ids.split(',') if x.strip()]
    except Exception:
        return {"error": True, "message": "Invalid ids parameter."}

    res = weather_service.delete_records(ids_list)
    return {"error": False, "result": res}
