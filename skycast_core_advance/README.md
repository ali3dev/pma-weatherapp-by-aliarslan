# SkyCast - Weather CRUD & Export API with Chainlit UI

This is my SkyCast project — a small but practical FastAPI backend with a Chainlit chat UI. It supports current weather lookups, a 5-day forecast, history CRUD, date-range record generation, batch deletes, and exports (JSON/CSV/PDF).

I wrote this to be easy to run locally and straightforward to extend. The following sections explain how the code is organized, how to run it, and why I chose certain algorithms.

---

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Architecture & Key Components](#architecture--key-components)
- [Tech Stack](#tech-stack)
- [Getting Started (Local Development)](#getting-started-local-development)
  - [Prerequisites](#prerequisites)
  - [Environment variables](#environment-variables)
  - [Install dependencies](#install-dependencies)
  - [Run the backend (FastAPI)](#run-the-backend-fastapi)
  - [Run the Chainlit UI](#run-the-chainlit-ui)
- [API Endpoints](#api-endpoints)
- [Chainlit UI Flows & Manual Tests](#chainlit-ui-flows--manual-tests)
- [Design Decisions & Rationale](#design-decisions--rationale)
- [Algorithms & Implementation Details](#algorithms--implementation-details)
- [Security, Secrets & Handling Private Files (EPO)](#security-secrets--handling-private-files-epo)
- [Edge Cases & Known Limitations](#edge-cases--known-limitations)
- [Testing & Validation](#testing--validation)
- [Troubleshooting](#troubleshooting)
- [Future Improvements](#future-improvements)
- [License & Attribution](#license--attribution)

---

## Project Overview
SkyCast is a sample service that demonstrates integrating a conversational UI (Chainlit) with a RESTful backend (FastAPI). The backend exposes weather and history management endpoints, interacts with the OpenWeather API for live data, and supports export capabilities in JSON, CSV and PDF. The Chainlit application provides a polished chat experience for querying weather, generating date-range records, managing history, and downloading exports directly from the chat.

This repository is intentionally small and focused on clarity, but built with conventions and practices you would see in production prototypes.

## Features
- Current weather and 5-day forecast lookups via OpenWeather.
- Persistent weather history stored in SQLite using SQLAlchemy.
- CRUD operations for history records (create, read, update, delete).
- Create date-range records by approximating per-day values from forecast data.
- Batch deletion of records via a single endpoint and Chainlit confirmation.
- Export history in JSON, CSV and PDF formats; streamed via FastAPI and attached in Chainlit UI for direct download.
- Chainlit UI interactions with robust session state handling and user-friendly prompts.

## Architecture & Key Components
- `app/main.py` — FastAPI application factory and route registration.
- `app/routes/` — FastAPI route handlers:
  - `weather_routes.py`: weather, forecast, create_range, record management.
  - `export_routes.py`: export endpoints returning `FileResponse` for streaming files.
- `app/services/` — Business logic separated from HTTP layer:
  - `weather_service.py`, `history_service.py`, `forecast_service.py`.
- `app/models/history_model.py` — SQLAlchemy ORM model for stored records.
- `app/database.py` — DB initialization and session management.
- `app/utils/` — small utilities: export generation, simple data structures.
- `chainlit_app.py` — Chainlit chat application, actions, and session-based flows.
- `exports/` — generated exports saved temporarily when streaming to Chainlit.

## Tech Stack
- Python 3.11+ (project tested with 3.12)
- FastAPI (REST API)
- Uvicorn (ASGI server)
- SQLAlchemy (ORM)
- SQLite (development persistence)
- Chainlit (chat UI)
- httpx (async HTTP client)
- python-dotenv (environment variables)
- fpdf2 (PDF export generation)

## Getting Started (Local Development)
### Prerequisites
- Python 3.11+ (3.12 recommended)
- Git
- An OpenWeather API key (free tier OK) — used for `/weather` and `/forecast` endpoints.

### Environment variables
Create a `.env` in the repository root with at least:

```
OPENWEATHER_API_KEY=your_openweather_api_key_here
BACKEND_URL=http://127.0.0.1:8000
```

`BACKEND_URL` defaults to `http://127.0.0.1:8000` if omitted.

### Install dependencies
Install the required packages. If you don't use virtualenv on this machine, just run the install command directly.

Windows (cmd.exe):

```bat
pip install --upgrade pip
pip install -r requirements.txt
```

### Run the backend (FastAPI)
From the project root:

```bat
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

This starts the API with automatic reload for development.

### Run the Chainlit UI
In a separate terminal (project root):

```bat
chainlit run chainlit_app.py --port 8001
```

Open the Chainlit UI in your browser (default http://localhost:8001) and interact with the SkyCast assistant.

## API Endpoints
All endpoints are documented with concise behaviors below. Use query parameters as shown.

- GET /
  - Returns a simple welcome JSON.

- GET /weather?location={location}
  - Fetch current weather from OpenWeather for `location` (city name, zip,country or coords).

- GET /forecast?location={location}
  - Returns a compact 5-day forecast list used to generate date-range records.

- GET /records
  - Returns all history records stored in the DB.

- PUT /update/{record_id}?desc={desc}
  - Update the `desc` of a given record.

- POST /delete/{record_id}
  - Delete a single record by ID.

- POST /delete_batch?ids=1,2,5-7
  - Delete multiple records by comma-separated IDs and numeric ranges.

- POST /create_range?location=...&start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
  - Creates daily records between `start_date` and `end_date` for `location`.

- GET /export/json, /export/csv, /export/pdf
  - Stream exported history in the requested format as a file download.

## Chainlit UI Flows & Manual Tests
Use the chat UI to test flows. Example interactions (copy/paste):

- Get current weather:
  - Type: `London` → Click `☀️ Current Weather`.

- Create date range records:
  - Type: `London` → Click `➕ Create Date Range Records` → Send `2025-10-10` → Send `2025-10-12`.

- View history:
  - Click `📜 History` → Use actions to update or delete records.

- Export:
  - Click `📦 Download Data` → Files will be attached to the chat for download.

## Design Decisions & Rationale
- Explicit service layer: keeps HTTP handlers thin and logic testable.
- Use `FileResponse` for exports: streams large files efficiently and sets correct headers for clients.
- Chainlit session flags: simple, lightweight state machine for multi-step flows (create-range, update, delete confirmation).
- SQLite + SQLAlchemy: low friction for prototypes, easy to swap to Postgres in production by updating the DB URL and a small connection config.

## Algorithms & Implementation Details
This section explains the concrete algorithmic choices and why they were selected. It is intended for engineers who will maintain or extend the project.

### 1) Date-Range Record Creation
- Goal: Given a `location`, `start_date`, and `end_date`, create daily weather records for each date in the inclusive interval.
- Source data: OpenWeather 5-day forecast (3-hour granularity). This repo uses a pragmatic approximation strategy:
  - Aggregation: group forecast points by date and compute the mean temperature for that day (simple arithmetic mean) and pick the most frequent weather description (mode) as the day's description.
  - Fallbacks: if the forecast doesn't cover all requested dates (e.g., range extends beyond available forecast) the service falls back to the current weather endpoint for missing days.
- Rationale: This approach gives reasonable per-day approximations without requiring paid historical data. It is simple, computationally cheap (O(n) over forecast points), and easy to test.

### 2) Batch Delete
- Goal: Allow users to delete many records in a single request safely and efficiently.
- Implementation:
  - Input parsing: Accept CSV and range syntax like `1,2,5-7` and expand ranges to explicit IDs.
  - Transactional deletion: wrap deletes in a DB transaction so partial failures can be rolled back or collected and reported back (we choose to attempt each delete and report failures to the client for visibility).
- Rationale: Parsing ranges makes the UI friendlier. Transactional semantics preserve data integrity; reporting failures keeps the operation observable.

### 3) Export Generation
- Formats: JSON (native), CSV (tabular), PDF (presentation using fpdf2).
- Implementation details:
  - JSON: write a compact JSON list of records.
  - CSV: use Python's csv module with explicit encoding (UTF-8) and proper quoting.
  - PDF: use a simple templating approach (fpdf2) with automatic page breaks and a small table rendering routine.
- Streaming: endpoints return `FileResponse` so clients receive a streamed download with proper headers.
- Rationale: These formats cover both data interchange (JSON, CSV) and human-readable snapshots (PDF). Streaming avoids loading large files entirely into memory.

### 4) Chainlit Session State Machine (Multi-step flows)
- Approach: Use `cl.user_session` keys as small boolean/holding-state flags for flows (e.g., `expecting_range_start`, `range_start`, `expecting_range_end`, `update_id`, `pending_delete_ids`).
- Why: Keeps the chat handler deterministic while remaining lightweight. No external state store is required for simple per-session flows.
- Caveat: This approach is fine for demo/prototype apps. For production-level multi-user flows, consider a structured storage (Redis) and stricter session expiry.

### 5) Complexity and Performance
- Most operations are O(n) where n is the size of returned forecast points or number of records processed for export/delete.
- SQLite is used for simplicity; for larger scale, migrate to a server DB and add indexes on frequently queried columns (e.g., `created_at`, `city`).

## Security, Secrets & Handling Private Files (EPO)
This project is intended for demonstration and small-team development. If you will be adding sensitive materials such as EPOs (electronic protected output), private keys, or API credentials, follow these rules strictly:

- Never commit secrets to version control. Use `.env` files locally and add them to `.gitignore`. A safe example file is provided as `.env.example`.
- Use a secrets manager for production (AWS Secrets Manager, Azure Key Vault, HashiCorp Vault, or your cloud provider equivalent).
- Store exported files that contain private data in secure, access-controlled storage (e.g., S3 with server-side encryption + restricted IAM policies). Do not keep private exports in the repository or in `exports/` without encryption and access controls.
- For local testing, place EPO or private files only in directories excluded by `.gitignore`. The repo `.gitignore` includes `exports/`, `.env`, and common virtualenv folders.
- Rotate keys and credentials regularly and minimize their scope (least privilege).

If you want me to upload your EPO into the project for local testing, provide it via a secure channel and I will:

1. Place it under a directory named `private/` (not committed), and add an entry in `.gitignore` to ensure it is never accidentally committed.
2. Add a README section explaining where the file lives locally and how to configure the app to use it (for example, a pointer in `.env` like `EPO_PATH=./private/my_epo_file`).
3. Optionally provide an encryption step for the file at rest (e.g., using GPG or symmetric encryption) and add instructions for decrypting during local dev.

Do NOT paste secrets into the chat. If you need help wiring the EPO into the code, tell me the filename and how you want it used; I will update config loading to reference `EPO_PATH` and ensure `.gitignore` prevents accidental commits.

---

## Edge Cases & Known Limitations
- Date-range creation uses the 5-day forecast to approximate daily values. For true historical data, integrate a historical weather API.
- No authentication: this sample app is not production-ready. Add OAuth2 / API keys for real deployments.
- Export files are saved to `exports/` temporarily when sending via Chainlit; a cleanup mechanism could be added.

## Testing & Validation
- Manual smoke tests are included in this repo's development notes.
- Suggested unit tests:
  - Service-level tests for `create_range`, `delete_records`, and export utilities.
  - Integration tests that spin up the FastAPI app via TestClient and validate endpoints.

## Troubleshooting
- Common issue: `OPENWEATHER_API_KEY` missing → `/weather` and `/forecast` return error payloads.
- If Chainlit displays `Chainlit context not found` when trying to attach files, ensure you call `cl.File` creation and sending inside the Chainlit runtime and not from a separate script.
- If uvicorn fails to import models, ensure `app.models` modules are imported before `Base.metadata.create_all()`; the repo already follows this order in `app/main.py`.

## Future Improvements
- Add authentication and per-user data separation.
- Replace SQLite with Postgres and add migrations via Alembic.
- Add comprehensive unit & integration tests with CI pipeline.
- Add background cleanup job to remove old export files.
- Improve UX: allow searching history, paginated endpoints, and richer export filters.

## License & Attribution
This project is provided as-is for learning and demonstration purposes.

---

If you'd like, I can also:
- Add a `private/` directory and a small helper that reads an `EPO_PATH` from `.env` (without committing the actual file).
- Add a small example script showing how to encrypt/decrypt EPO files for local storage.

Tell me whether you want me to add the `private/` folder and helper wiring (I will add `.gitignore` entries and update `.env.example`).


