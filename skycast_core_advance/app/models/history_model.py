from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.database import Base

class WeatherRecord(Base):
    __tablename__ = "weather_records"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String)
    temp = Column(Float)
    desc = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
