# 🌤️ SkyCast Core — PMA Weather App (Tech Assessment #1)

## Overview

**SkyCast Core** is a modular backend and chat-based interface for delivering live weather conditions and 5-day forecasts using the [OpenWeatherMap API](https://openweathermap.org/api). Developed for the PMA Bootcamp (AI Engineer Tech Assessment #1), it demonstrates clean API design, asynchronous processing, and a scalable code structure.

- **Flexible location input:** Accepts city names, ZIP/postal codes, and GPS coordinates.
- **Conversational UI:** Built with Chainlit for interactive, chat-like weather queries.
- **Robust backend:** FastAPI powers reliable, fast API endpoints.
- **Smart fallback:** Uses IP-based geolocation when no explicit location is provided.

---

## 🧠 Features

- **Multi-format location input**
  - City/Town name (e.g., `Lahore`, `New York`)
  - ZIP/Postal code with country code (e.g., `94040,US`)
  - GPS coordinates (e.g., `31.5497,74.3436`)
- **Returns**
  - Current weather conditions
  - 5-day forecast (daily averages)
  - Fallback to IP geolocation when location is missing
- **Other Highlights**
  - Conversational Chainlit interface
  - Modular FastAPI backend: clear separation of routes, services, and utilities

---

## ⚙️ Tech Stack

| Layer             | Tools / Libraries        |
|-------------------|-------------------------|
| **Backend**       | FastAPI, Uvicorn        |
| **Chat Frontend** | Chainlit                |
| **Data Source**   | OpenWeatherMap API      |
| **Networking**    | httpx, requests         |
| **Env Mgmt**      | python-dotenv           |
| **Language**      | Python 3.12             |

---

## 🧩 Project Structure

```
skycast_core/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── routes/
│   │   ├── weather_routes.py
│   │   └── forecast_routes.py
│   ├── services/
│   │   ├── weather_service.py
│   │   └── forecast_service.py
│   └── utils/
│       └── geolocation.py
├── chainlit_app.py
├── requirements.txt
├── .env               # API key (NOT committed)
└── README.md
```

---

## 📦 Requirements

- Python 3.10+ (3.12 recommended)
- pip

---

## 🔑 Environment Variables

Create a `.env` file in the project root and set your API key:

```env
OPENWEATHER_API_KEY=your_openweather_api_key_here
# Optional: if backend runs elsewhere
# BACKEND_URL=http://127.0.0.1:8000
```

---

## 🚀 Local Development Setup

1. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

2. **Start the backend (FastAPI / Uvicorn):**
    ```sh
    # Set the API key in your environment or ensure .env is configured
    uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
    ```
    - API documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

3. **Run the Chainlit chat UI (in a second terminal):**
    ```sh
    chainlit run chainlit_app.py -w --port 8001
    ```
    - Chat UI: [http://localhost:8001](http://localhost:8001)

---

## 📡 API Endpoints

| Endpoint                                | Description           | Example Input         |
|------------------------------------------|-----------------------|----------------------|
| `/weather?location=Lahore`               | Current weather       | City name            |
| `/weather?location=94040,US`             | By ZIP code           | ZIP + country code   |
| `/weather?location=31.5497,74.3436`      | By GPS coordinates    | lat,long             |
| `/forecast?...`                         | 5-day forecast        | Same params          |

---

## 💬 Chainlit Interface

- Enter any valid location in the chat.
- Choose between "Current Weather" or "5-Day Forecast".
- Results are presented in a conversational format, with enhanced readability and emoji highlights.

---

## 🧾 Submission Context

- **Task:** Tech Assessment #1 – Weather App
- **Implements:** Real API integration, multi-format location input
- **Not included:** UI icons, map embeds
- **Next step:** Add CRUD operations and database persistence (Tech Assessment #2)

---

## 🛠️ Troubleshooting

- **Chainlit validation error for Actions:**  
  Ensure your Chainlit code uses `cl.Action(..., payload={...}, label=...)`.  
  This repo's `chainlit_app.py` uses payload-based actions.

- **OPENWEATHER_API_KEY missing:**  
  Confirm `.env` is in the project root and contains the API key.  
  Or set it in the terminal before starting:  
  `export OPENWEATHER_API_KEY=...` (Linux/macOS)  
  `set OPENWEATHER_API_KEY=...` (Windows)

- **Backend unreachable from Chainlit:**  
  Ensure the backend is running and `BACKEND_URL` is set correctly for Chainlit.

- **Testing suggestions:**  
  - Unit tests with `pytest`
  - Mock external HTTP (OpenWeather) with `respx` or `requests-mock`

---

## 👤 Author

**Ali Arslan Khan**  
Generative & Agentic AI Engineer  
📧 aliarslan5866@gmail.com

---

_If you find this project helpful, please ⭐️ star the repository!_
