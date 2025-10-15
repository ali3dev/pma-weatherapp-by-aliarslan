# SkyCast - Weather CRUD & Export API with Chainlit UI

Welcome to **SkyCast** – a practical, extensible FastAPI backend combined with a Chainlit chat UI for real-time weather queries, history management, and data exports. Designed for clarity, reliability, and ease of local development, SkyCast demonstrates how to build a conversational weather application with modern Python tooling.

---

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Architecture & Key Components](#architecture--key-components)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Environment Variables](#environment-variables)
  - [Install Dependencies](#install-dependencies)
  - [Run the Backend](#run-the-backend)
  - [Run the Chainlit UI](#run-the-chainlit-ui)
- [API Endpoints](#api-endpoints)
- [Chainlit UI Flows & Manual Tests](#chainlit-ui-flows--manual-tests)
- [Design Decisions](#design-decisions)
- [Algorithms & Implementation Details](#algorithms--implementation-details)
- [Security & Secrets Management](#security--secrets-management)
- [Edge Cases & Known Limitations](#edge-cases--known-limitations)
- [Testing & Validation](#testing--validation)
- [Troubleshooting](#troubleshooting)
- [Future Improvements](#future-improvements)
- [License & Attribution](#license--attribution)

---

## Project Overview

SkyCast integrates a RESTful backend (FastAPI) with a conversational chat UI (Chainlit). The backend exposes endpoints for weather lookups, a 5-day forecast, historical CRUD, batch record deletion, and exports in JSON/CSV/PDF formats. The Chainlit frontend enables interactive weather queries, history management, and file downloads directly within the chat.

This repository is intentionally compact, demonstrating production-grade conventions in a prototype-friendly package.

## Features

- **Current Weather & Forecasts:** Live data via OpenWeather integration.
- **Persistent History:** Store, update, and delete records in SQLite.
- **Batch Operations:** Efficient multi-record deletion and date-range record creation.
- **Export Functionality:** Download history in JSON, CSV, or PDF formats.
- **Conversational UI:** Chainlit-powered chat interface for seamless interaction.
- **Robust Session State:** Reliable multi-step flows in the UI.

## Architecture & Key Components

- `app/main.py`: FastAPI application factory and route registration.
- `app/routes/`: Route handlers for weather, forecast, record management, and exports.
- `app/services/`: Business logic isolated from HTTP layer.
- `app/models/`: SQLAlchemy ORM models.
- `app/database.py`: Database initialization and session management.
- `app/utils/`: Utilities for export generation and data manipulation.
- `chainlit_app.py`: Chainlit chat application and session flows.
- `exports/`: Temporary storage for exported files.

## Tech Stack

- Python 3.11+ (tested with 3.12)
- FastAPI (REST API)
- Uvicorn (ASGI server)
- SQLAlchemy (ORM)
- SQLite (development DB)
- Chainlit (chat UI)
- httpx (async HTTP client)
- python-dotenv (env vars)
- fpdf2 (PDF export generation)

## Getting Started

### Prerequisites

- Python 3.11+ (3.12 recommended)
- Git
- OpenWeather API key (free tier supported)

### Environment Variables

Create a `.env` file in your repo root:

```
OPENWEATHER_API_KEY=your_openweather_api_key_here
BACKEND_URL=http://127.0.0.1:8000
```

### Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Run the Backend

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Run the Chainlit UI

```bash
chainlit run chainlit_app.py --port 8001
```

Open your browser at [http://localhost:8001](http://localhost:8001) to interact with SkyCast.

## API Endpoints

- `GET /`: Welcome message.
- `GET /weather?location={location}`: Current weather lookup.
- `GET /forecast?location={location}`: 5-day forecast.
- `GET /records`: Retrieve all history records.
- `PUT /update/{record_id}?desc={desc}`: Update record description.
- `POST /delete/{record_id}`: Delete a single record.
- `POST /delete_batch?ids=1,2,5-7`: Batch deletion by IDs.
- `POST /create_range?location=...&start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`: Create records by date range.
- `GET /export/json|csv|pdf`: Download history in specified format.

## Chainlit UI Flows & Manual Tests

- **Current Weather:** Type a city name and click ☀️ Current Weather.
- **Create Date-Range Records:** Type a city, click ➕ Create Date Range Records, then provide start/end dates.
- **View/Manage History:** Click 📜 History to update or delete records.
- **Export Data:** Click 📦 Download Data for file attachments.

## Design Decisions

- **Explicit Service Layer:** Keeps HTTP endpoints thin and testable.
- **Streaming Exports:** Efficiently serve large files with proper headers.
- **Session State in Chainlit:** Enables reliable, lightweight multi-step flows.
- **SQLite for Prototyping:** Easy to swap for Postgres in production.

## Algorithms & Implementation Details

### Date-Range Record Creation

- Aggregates OpenWeather 5-day forecast (3-hour intervals) into daily summaries.
- Fallback to current weather for missing dates.
- Simple, efficient (O(n)), and easy to test.

### Batch Delete

- Accepts comma-separated and range syntax (e.g., `1,2,5-7`).
- Transactional deletion with failure reporting.

### Export Generation

- **JSON:** Compact list.
- **CSV:** Tabular with UTF-8 encoding.
- **PDF:** Tabular presentation using fpdf2.
- All exports stream via FastAPI for efficient downloads.

### Chainlit Session State

- Uses per-session flags for multi-step operations.
- No external state store required for prototypes.

## Security & Secrets Management

- **Never commit secrets:** Use `.env`, which is `.gitignore`d.
- **Production:** Use a secrets manager (AWS, Azure, Vault, etc.).
- **Private Files:** Store sensitive exports securely; encrypt for local testing.
- **Key Rotation:** Regularly update credentials.

## Edge Cases & Known Limitations

- Date-range creation uses forecast data; true historical data requires a paid API.
- No authentication (add OAuth2 or API keys for production).
- Export cleanup is manual (consider an automatic job).

## Testing & Validation

- Manual smoke tests.
- Suggested: Unit tests for services, integration tests with FastAPI TestClient.

## Troubleshooting

- Missing `OPENWEATHER_API_KEY`: Weather endpoints fail.
- Chainlit file attachment issues: Ensure file creation/sending runs within Chainlit runtime.
- Uvicorn import errors: Confirm models are imported before DB initialization.

## Future Improvements

- Authentication and per-user data separation.
- PostgreSQL migration and Alembic migrations.
- CI/CD and comprehensive testing.
- Automatic export cleanup.
- Enhanced UX: search, pagination, filters.


If you find this project helpful, please ⭐️ star the repository!
