from fastapi import APIRouter
from app.services.history_service import get_all_history, delete_history

router = APIRouter(prefix="/history")

@router.get("/")
def read_history(sort: bool = False):
    data = get_all_history(sort=sort)
    return {"count": len(data), "records": [
        {"id": d.id, "city": d.city, "temp": d.temp, "desc": d.desc} for d in data
    ]}


@router.delete("/{record_id}")
def remove_history(record_id: int):
    success = delete_history(record_id)
    return {"deleted": success}
