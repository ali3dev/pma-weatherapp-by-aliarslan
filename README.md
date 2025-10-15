# 🌤️ PMA Weather App — SkyCast Core & CRUD/Export API

Welcome! This repository showcases two modular weather app projects built for the PMA Bootcamp (AI Engineer Tech Assessment). Both apps use FastAPI and Chainlit for delivering interactive weather queries, but each demonstrates different backend features and API capabilities.

---

## 📁 Structure

- `skycast_core/` — PMA Weather App (Tech Assessment #1):
  - Modular FastAPI backend with Chainlit chat UI.
  - Focuses on live weather and 5-day forecasts via OpenWeatherMap.
  - Flexible location input (city, ZIP, GPS) and smart IP fallback.

- `skycast_crud_export/` — Weather CRUD & Export API (Tech Assessment #2):
  - Adds persistent history (SQLite), batch record operations, and export features (JSON/CSV/PDF).
  - Enhanced Chainlit UI for managing, viewing, and downloading weather data.

Each folder includes its own `README.md` with detailed instructions, setup, and features. **Do not remove or overwrite those files.**

---

## 🚀 What Does This Repo Do?

This repo demonstrates:

- **Clean API Design:** FastAPI powers robust, well-structured HTTP endpoints.
- **Conversational UIs:** Chainlit enables interactive, chat-style weather queries.
- **Multi-format Location Input:** Accepts city/town names, ZIP/postal codes, and GPS coordinates.
- **Live Weather & Forecasts:** Integrates OpenWeatherMap for real-time weather and 5-day averages.
- **Smart Fallback:** Uses IP-based geolocation when explicit location is missing.
- **Asynchronous Processing:** High-performance networking with httpx and requests.
- **Modular Code Architecture:** Clear separation of routes, services, and utilities.
- **History & CRUD Operations (CRUD/Export module):** SQLite-backed record storage, updates, batch deletion, and data exports.
- **Export Capabilities:** Download history as JSON, CSV, or PDF (CRUD/Export module).
- **Best Practices:** Secure env management (`.env`), production-grade conventions, clear troubleshooting, and next-step suggestions.

---

## 🧩 Tech Stack

| Layer           | Tools / Libraries              |
|-----------------|-------------------------------|
| Backend         | FastAPI, Uvicorn, SQLAlchemy  |
| Chat Frontend   | Chainlit                      |
| Data Source     | OpenWeatherMap API            |
| Database        | SQLite                        |
| Networking      | httpx, requests               |
| Export          | fpdf2                         |
| Env Mgmt        | python-dotenv                 |
| Language        | Python 3.12                   |

---

## 📦 Requirements

- Python 3.11+ (3.12 recommended)
- pip
- OpenWeather API Key

---

## 🔑 Environment Variables

Create a `.env` file in the project root and set:

```
OPENWEATHER_API_KEY=your_openweather_api_key_here
# Optional for Chainlit UI (crud/export module):
BACKEND_URL=http://127.0.0.1:8000
```

---

## 🛠️ Setup & Usage

See each folder’s `README.md` for full instructions!

**General steps:**
1. Install dependencies:  
   `pip install -r requirements.txt`
2. Start FastAPI backend:  
   `uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload`
3. Run Chainlit UI (separate terminal):  
   `chainlit run chainlit_app.py --port 8001`
4. Interact via browser:  
   [http://localhost:8001](http://localhost:8001)

---

## 📡 API Endpoints (highlights)

- `/weather?location=...` — Current weather (city, ZIP, GPS)
- `/forecast?location=...` — 5-day forecast
- `/records` — View history (**CRUD/Export**)
- `/update/{record_id}` — Update record (**CRUD/Export**)
- `/delete_batch?ids=...` — Batch deletion (**CRUD/Export**)
- `/export/json|csv|pdf` — Download history (**CRUD/Export**)

---

## 🧠 Features

- **Multi-format location input**
- **Live weather + 5-day forecasts**
- **Conversational chat UI**
- **Modular backend**
- **IP geolocation fallback**
- **CRUD/history management** (CRUD/Export)
- **Export in JSON, CSV, PDF** (CRUD/Export)
- **Robust session flows**
- **Production-grade code practices**

---

## 🧑‍💻 Author

**Ali Arslan Khan**  
Generative & Agentic AI Engineer  
📧 aliarslan5866@gmail.com

If you found this project helpful, please ⭐️ star the repository!

---

## 📚 More Info

- For **detailed documentation, troubleshooting, and manual tests**, see the `README.md` inside each folder.
- Each module is standalone and can be developed/run independently.
