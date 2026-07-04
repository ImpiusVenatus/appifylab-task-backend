# Buddy Script Backend

FastAPI API for the Buddy Script social app (AppifyLab full-stack engineer task). Uses **NeonDB** (serverless PostgreSQL).

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

## Database migrations

Requires `DATABASE_URL` in `.env` pointing to your Neon database.

```bash
# Apply all migrations
alembic upgrade head

# Create a new migration after model changes
alembic revision --autogenerate -m "describe change"
```

## Health check

```bash
curl http://localhost:8000/api/v1/health
```

Returns `status: ok` when the database is reachable, or `degraded` if Neon is not configured yet.

## Auth API (JWT in httpOnly cookies)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/register` | Create account (first name, last name, email, password) |
| `POST` | `/api/v1/auth/login` | Sign in |
| `POST` | `/api/v1/auth/logout` | Clear auth cookie |
| `GET` | `/api/v1/auth/me` | Current user (requires cookie) |

Tokens are signed JWTs stored in an httpOnly cookie — not session rows in the database.

## Posts API

Requires auth cookie. Images are stored on [Cloudinary](https://cloudinary.com) (free tier works for local development).

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/posts` | Create a post (`multipart/form-data`: `content`, `visibility`, optional `image`) |
| `GET` | `/api/v1/posts` | Paginated feed (`limit`, `offset`) — public posts plus your private posts |

`visibility` is `public` (everyone) or `private` (author only).

## Comments API

Requires auth cookie. Replies use the same create endpoint with `parent_id` set.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/posts/{post_id}/comments` | List comments and nested replies for a post |
| `POST` | `/api/v1/posts/{post_id}/comments` | Create a comment or reply (`content`, optional `parent_id`) |

## Environment variables

| Variable | Description |
|----------|-------------|
| `FRONTEND_URL` | Next.js origin for CORS (default `http://localhost:3000`) |
| `DATABASE_URL` | Neon PostgreSQL connection string |
| `JWT_SECRET` | Secret for signing tokens (auth phases) |
| `COOKIE_*` | httpOnly cookie settings for JWT auth |
| `CLOUDINARY_*` | Cloudinary credentials for post image uploads |
| `MAX_UPLOAD_SIZE_MB` | Max image upload size (default `5`) |

## Project structure

```
backend/
├── alembic/              # Database migrations
├── app/
│   ├── main.py           # FastAPI app entry
│   ├── config.py         # Settings from .env
│   ├── database.py       # SQLAlchemy + Neon connection
│   ├── deps.py           # Auth dependencies (get_current_user)
│   ├── security.py       # Password hashing + JWT helpers
│   ├── routers/
│   │   ├── v1.py         # /api/v1 router (health + versioned routes)
│   │   ├── auth.py       # Register, login, logout, me
│   │   └── posts.py      # Create and list posts
│   ├── services/
│   │   └── cloudinary.py # Image upload helper
│   └── models/
│       ├── user.py       # User model (auth)
│       ├── post.py       # Post model
│       ├── comment.py    # Comment + reply model
│       └── like.py       # Polymorphic likes
├── requirements.txt
└── .env.example
```
