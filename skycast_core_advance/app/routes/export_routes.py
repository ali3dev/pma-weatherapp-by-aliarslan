from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.database import SessionLocal
from app.models.history_model import WeatherRecord
from app.utils.export_utils import export_data
import os
import mimetypes

router = APIRouter(prefix="/export")


@router.get("/{format_type}")
def export_records(format_type: str):
    db = SessionLocal()
    records = db.query(WeatherRecord).all()
    db.close()

    if not records:
        raise HTTPException(status_code=404, detail="No records found to export.")

    data = [{"id": r.id, "city": r.city, "temp": r.temp, "desc": r.desc} for r in records]
    os.makedirs("exports", exist_ok=True)
    # export_utils will add the extension, so pass a base filename without extension
    filename_base = "exports/weather_records"

    export_data(data, format_type=format_type, filename=filename_base)

    filename = f"{filename_base}.{format_type}"

    if not os.path.exists(filename):
        raise HTTPException(status_code=500, detail="Export failed, file not found.")

    # Determine mime type
    mime_type, _ = mimetypes.guess_type(filename)
    if not mime_type:
        mime_type = "application/octet-stream"

    return FileResponse(path=filename, media_type=mime_type, filename=os.path.basename(filename))
