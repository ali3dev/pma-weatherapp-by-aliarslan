from app.database import SessionLocal
from app.models.history_model import WeatherRecord
from app.utils.dsa_structures import sort_history_by_temp

def get_all_history(sort=False):
    db = SessionLocal()
    records = db.query(WeatherRecord).all()
    if sort:
        records = sort_history_by_temp(records)
    db.close()
    return records

def delete_history(record_id: int):
    db = SessionLocal()
    record = db.query(WeatherRecord).filter(WeatherRecord.id == record_id).first()
    if record:
        db.delete(record)
        db.commit()
        db.close()
        return True
    db.close()
    return False
