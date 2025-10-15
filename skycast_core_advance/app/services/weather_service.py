import requests, os
from dotenv import load_dotenv
from app.database import SessionLocal
from app.models.history_model import WeatherRecord
from app.utils.dsa_structures import Stack
from app.utils.export_utils import export_data

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

# CREATE + READ helpers
def get_current_weather(location: str):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={API_KEY}&units=metric"
    res = requests.get(url)
    if res.status_code != 200:
        return {"error": True, "message": "Invalid location or API issue."}
    data = res.json()

    db = SessionLocal()
    record = WeatherRecord(city=data["name"], temp=data["main"]["temp"], desc=data["weather"][0]["description"])
    db.add(record)
    db.commit()
    db.refresh(record)
    db.close()

    return {"error": False, "data": data}


def get_all_records():
    db = SessionLocal()
    records = db.query(WeatherRecord).all()
    db.close()
    stack = Stack()
    for r in records:
        stack.push({"id": r.id, "city": r.city, "temp": r.temp, "desc": r.desc})
    return {"count": len(records), "records": stack.items}


def update_record(record_id: int, new_desc: str):
    db = SessionLocal()
    record = db.query(WeatherRecord).filter(WeatherRecord.id == record_id).first()
    if not record:
        db.close()
        return {"error": True, "message": "Record not found."}
    record.desc = new_desc
    db.commit()
    db.refresh(record)
    db.close()
    return {"error": False, "message": "Updated successfully."}


def delete_record(record_id: int):
    db = SessionLocal()
    record = db.query(WeatherRecord).filter(WeatherRecord.id == record_id).first()
    if not record:
        db.close()
        return {"error": True, "message": "Record not found."}
    db.delete(record)
    db.commit()
    db.close()
    return {"error": False, "message": "Deleted successfully."}


def delete_records(ids: list):
    """
    Delete multiple records by ID. Returns summary dict with deleted ids and failed ids.
    """
    db = SessionLocal()
    deleted = []
    failed = {}

    try:
        for rid in ids:
            record = db.query(WeatherRecord).filter(WeatherRecord.id == rid).first()
            if record:
                db.delete(record)
                deleted.append(rid)
            else:
                failed[rid] = "not found"
        db.commit()
    except Exception as e:
        db.rollback()
        # mark all as failed if transaction fails
        for rid in ids:
            if rid not in deleted:
                failed[rid] = str(e)
    finally:
        db.close()

    return {"deleted": deleted, "failed": failed}


def create_range(location: str, start_date: str, end_date: str):
    """
    Create records for each date in the range [start_date, end_date].
    Uses the 5-day forecast as an approximation when available.
    Dates must be in YYYY-MM-DD format.
    """
    from datetime import datetime, timedelta
    from app.services.forecast_service import get_forecast

    # validate dates
    try:
        sd = datetime.strptime(start_date, "%Y-%m-%d").date()
        ed = datetime.strptime(end_date, "%Y-%m-%d").date()
    except Exception:
        return {"error": True, "message": "Dates must be in YYYY-MM-DD format."}

    if sd > ed:
        return {"error": True, "message": "start_date must be <= end_date."}

    # get forecast approximation
    fc = get_forecast(location)
    if fc.get("error"):
        return {"error": True, "message": "Could not fetch forecast to approximate daily temps."}

    forecast_map = {f["date"]: f for f in fc.get("forecast", [])}

    db = SessionLocal()
    created = 0
    d = sd
    while d <= ed:
        ds = d.isoformat()
        if ds in forecast_map:
            temp = forecast_map[ds]["temp"]
            desc = forecast_map[ds]["description"]
        else:
            # fallback: use current weather for the location as approximation
            try:
                import requests, os
                url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={API_KEY}&units=metric"
                res = requests.get(url)
                if res.status_code == 200:
                    jd = res.json()
                    temp = jd["main"]["temp"]
                    desc = jd["weather"][0]["description"]
                else:
                    temp = None
                    desc = "unknown"
            except Exception:
                temp = None
                desc = "unknown"

        record = WeatherRecord(city=location, temp=temp if temp is not None else 0.0, desc=desc)
        db.add(record)
        created += 1
        d = d + timedelta(days=1)

    db.commit()
    db.close()

    return {"error": False, "message": f"Created {created} records for {location} between {start_date} and {end_date}."}
