# AppifyLab Backend

FastAPI API for the AppifyLab full-stack engineer task. Uses **NeonDB** (serverless PostgreSQL).

## Prerequisites

- Python 3.11+
- A [Neon](https://neon.tech) project with a PostgreSQL connection string

## Setup

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set `DATABASE_URL` to your Neon connection string.

## Run

```bash
fastapi dev app/main.py
```

On Windows, if you see a `UnicodeEncodeError` from the FastAPI CLI, run with UTF-8 enabled:

```bash
set PYTHONUTF8=1
fastapi dev app/main.py
```

API runs at `http://localhost:8000`. Interactive docs: `http://localhost:8000/docs`.

## Health check

```bash
curl http://localhost:8000/api/health
```

Returns `status: ok` when the database is reachable, or `degraded` if Neon is not configured yet.

## Environment variables

| Variable | Description |
|----------|-------------|
| `FRONTEND_URL` | Next.js origin for CORS (default `http://localhost:3000`) |
| `DATABASE_URL` | Neon PostgreSQL connection string |
| `JWT_SECRET` | Secret for signing tokens (auth phases) |
| `COOKIE_*` | httpOnly cookie settings for JWT auth |

## Project structure

```
backend/
├── app/
│   ├── main.py       # FastAPI app entry
│   ├── config.py     # Settings from .env
│   └── database.py   # SQLAlchemy + Neon connection
├── requirements.txt
└── .env.example
```
