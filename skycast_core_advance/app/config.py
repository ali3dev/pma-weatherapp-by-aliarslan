import os
from dotenv import load_dotenv
load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
DB_URL = os.getenv("DB_URL", "sqlite:///./weather_history.db")
