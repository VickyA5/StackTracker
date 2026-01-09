# StackTracker Backend

This backend uses FastAPI + SQLAlchemy. Tests cover the user creation endpoint.

## Prerequisites
- Python 3.10+
- PowerShell or a shell (WSL/Linux/macOS)

## Setup (Windows PowerShell)
```powershell
# From repo root
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r back\requirements.txt
```

## Setup (WSL/Linux/macOS)
```bash
# From repo root
python3 -m venv .venv
source .venv/bin/activate
pip install -r back/requirements.txt
```

## Run Tests
The tests set up a temporary SQLite database automatically; no manual `DATABASE_URL` needed.

```powershell
# Windows PowerShell
pytest back\tests -q
```

```bash
# WSL/Linux/macOS
pytest back/tests -q
```

## What’s Tested
- Creating a new user returns 201 with `id` and `username`.
- Creating a duplicate username returns 409 with a clear message.
- Payload validation errors return 422.

## Troubleshooting
- Execution policy: If PowerShell blocks script activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and retry.
- If `psycopg2-binary` install fails, you can skip it for tests (SQLite is used); but keep it for Postgres in development.

## Docker Compose (API + Postgres)
This starts the API on port 8000 and a Postgres database on port 5432.

```bash
# From repo root
docker compose up -d --build

# View API logs
docker compose logs -f api

# Stop services
docker compose down
```

The API will be available at http://localhost:8000 and exposes:
- POST /api/users

The API uses `DATABASE_URL` injected by Compose:
`postgresql+psycopg2://stackuser:stackpass@db:5432/stacktracker`.
