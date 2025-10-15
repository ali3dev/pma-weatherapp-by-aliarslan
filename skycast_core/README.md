# 🌤️ SkyCast Core — Weather App

SkyCast Core is a small backend + conversational UI that provides current weather and a 5‑day forecast using OpenWeatherMap.  
This repo was created for the PMA Bootcamp Tech Assessment and demonstrates a modular FastAPI backend with a Chainlit chat UI.

TL;DR
- Backend: FastAPI (app/)
- Frontend / chat UI: Chainlit (`chainlit_app.py`)
- Run backend on port 8000 and Chainlit UI on port 8001 (separate terminals)

Features
- Current weather by city or ZIP
- 5‑day forecast (daily summary)
- IP-based fallback geolocation when no location provided
- Clean modular structure: routes → services → utils

Tech stack
- Python 3.12
- FastAPI, Uvicorn
- Chainlit, httpx
- python-dotenv, requests

Project structure

skycast_core/
├── app/
│ ├── main.py
│ ├── config.py
│ ├── routes/
│ │ └── weather_routes.py
│ ├── services/
│ │ └── weather_service.py
│ └── utils/
│ └── geolocation.py
├── chainlit_app.py
├── .env # local (should NOT be committed)
├── requirements.txt
└── README.md


Requirements
- Python 3.10+ (3.12 recommended)
- pip
- Windows cmd.exe examples below (adjust for PowerShell / macOS / Linux)

Setup (Windows, cmd.exe)
```cmd
# create and activate venv
python -m venv .venv
.\\.venv\\Scripts\\activate

# install dependencies
pip install -r [requirements.txt](http://_vscodecontentref_/8)


Environment variables
Create a .env file in the project root with at least:

OPENWEATHER_API_KEY=your_openweather_api_key_here
# Optional: if backend runs elsewhere
# BACKEND_URL=http://127.0.0.1:8000

Run (development)

Start the backend (FastAPI / Uvicorn):

set OPENWEATHER_API_KEY=your_openweather_api_key_here
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

Backend docs: http://127.0.0.1:8000/docs

Start Chainlit UI in a second terminal:

set BACKEND_URL=http://127.0.0.1:8000
chainlit run [chainlit_app.py](http://_vscodecontentref_/9) -w --port 8001

Chainlit UI: http://localhost:8001

Quick API examples

Current weather:
GET http://127.0.0.1:8000/weather?location=Lahore

Forecast:
GET http://127.0.0.1:8000/forecast?location=New%20York

Example response (current weather)

{
  "error": false,
  "data": {
    "name": "New York",
    "main": {
      "temp": 16.5,
      "humidity": 75
    },
    "weather": [
      {"description": "overcast clouds"}
    ]
  }
}


Troubleshooting:- 

Chainlit validation error for Actions:

If you see a pydantic validation error about Action.payload, ensure your Chainlit code uses cl.Action(..., payload={...}, label=...). This repo's chainlit_app.py uses payload-based actions.

OPENWEATHER_API_KEY missing:

Confirm .env is in the project root and contains OPENWEATHER_API_KEY.
Or set it in the terminal before starting: set OPENWEATHER_API_KEY=...
Backend unreachable from Chainlit:
Ensure backend is running and BACKEND_URL is set correctly for Chainlit.
Test directly: curl "http://127.0.0.1:8000/weather?location=London" or use a Python snippet with httpx.

Use uvicorn --reload in dev.
Logging: Chainlit logs appear in the terminal where you start it; add structured logging in app for backend traceability.
Testing suggestions:
Unit tests with pytest.
Mock external HTTP (OpenWeather) with respx or requests-mock.


Author:- 

Ali Arslan Khan
Agentic & Generative AI Engineer.
aliarslan5866@gmail.com



🔗 GitHub Repository: [pma-weatherapp-by-aliarslan](https://github.com/ali3dev/pma-weatherapp-by-aliarslan)
