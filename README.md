# Buddy Script Backend

FastAPI API for the **Buddy Script** social feed (AppifyLab full-stack engineer task).

Stack: **FastAPI**, **SQLAlchemy**, **Neon/Railway PostgreSQL**, **JWT httpOnly cookies**, **Cloudinary** for images.

## Features

- User registration and login (first name, last name, email, password)
- JWT auth stored in httpOnly cookies
- Profile avatar upload (Cloudinary)
- Posts with text, optional image, public/private visibility
- Paginated feed (newest first)
- Comments and nested replies
- Likes on posts and comments, with who-liked listing
- Delete own posts; delete own comments or comments on your posts

## Prerequisites

- Python 3.11+ (3.12 recommended)
- PostgreSQL database ([Neon](https://neon.tech) or Railway Postgres)
- [Cloudinary](https://cloudinary.com) account (free tier works)

## Local setup

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

Edit `.env`:

1. Set `DATABASE_URL` to your Postgres connection string.
2. Set `JWT_SECRET` to a long random string.
3. Set Cloudinary credentials for image uploads.

Apply migrations and start the API:

```bash
alembic upgrade head
fastapi dev app/main.py
```

API: `http://localhost:8000`  
Swagger docs: `http://localhost:8000/docs`

On Windows, if the FastAPI CLI hits a Unicode error:

```bash
set PYTHONUTF8=1
fastapi dev app/main.py
```

## Deploy on Railway

1. Create a new Railway project and connect this repository.
2. Set the **Root Directory** to `backend` (important — the FastAPI app lives in `app/`).
3. Add environment variables from `.env.example` (see production section below).
4. Railway reads `railway.toml` and runs:
   - `alembic upgrade head`
   - `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Health check: `GET /api/v1/health`

`Procfile` and `runtime.txt` are included as fallbacks for other PaaS hosts.

### Production environment variables

| Variable | Example | Notes |
|----------|---------|-------|
| `DATABASE_URL` | `postgresql://...` | Neon or Railway Postgres |
| `JWT_SECRET` | long random string | Required |
| `FRONTEND_URL` | `https://your-app.vercel.app` | Primary frontend origin |
| `CORS_ALLOWED_ORIGINS` | `https://your-app.vercel.app` | Comma-separated if you have preview URLs too |
| `COOKIE_SECURE` | `true` | Required over HTTPS |
| `COOKIE_SAMESITE` | `none` | Required when frontend and API are on different domains |
| `CLOUDINARY_*` | from Cloudinary dashboard | Required for uploads |

Set the frontend `NEXT_PUBLIC_API_URL` to your Railway public URL (e.g. `https://your-api.up.railway.app`).

### CORS

The API allows credentialed requests from origins listed in `CORS_ALLOWED_ORIGINS`. If that variable is empty, only `FRONTEND_URL` is allowed.

For local dev:

```env
FRONTEND_URL=http://localhost:3000
COOKIE_SECURE=false
COOKIE_SAMESITE=lax
```

For Vercel + Railway:

```env
FRONTEND_URL=https://your-app.vercel.app
CORS_ALLOWED_ORIGINS=https://your-app.vercel.app
COOKIE_SECURE=true
COOKIE_SAMESITE=none
```

## Database migrations

```bash
alembic upgrade head
alembic revision --autogenerate -m "describe change"   # after model changes
```

Migrations:

| Revision | Description |
|----------|-------------|
| `001_create_users` | Users table |
| `002_create_feed_tables` | Posts, comments, likes |
| `003_add_user_avatar` | `avatar_url`, `avatar_public_id` on users |

## API reference

All routes are under `/api/v1`. Protected routes require the `access_token` httpOnly cookie.

### Health

| Method | Endpoint | Auth |
|--------|----------|------|
| `GET` | `/health` | No |

### Auth

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/register` | Create account |
| `POST` | `/auth/login` | Sign in (sets cookie) |
| `POST` | `/auth/logout` | Clear cookie |
| `GET` | `/auth/me` | Current user |
| `POST` | `/auth/me/avatar` | Upload profile photo (`multipart/form-data`, field `avatar`) |

### Posts

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/posts` | Create post (`multipart/form-data`: `content`, `visibility`, optional `image`) |
| `GET` | `/posts` | Feed (`limit`, `offset`) — public posts + your private posts |
| `DELETE` | `/posts/{post_id}` | Delete own post (removes Cloudinary image if present) |

`visibility`: `public` | `private`

### Comments

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/posts/{post_id}/comments` | List comments and replies |
| `POST` | `/posts/{post_id}/comments` | Create comment or reply (`content`, optional `parent_id`) |
| `DELETE` | `/posts/{post_id}/comments/{comment_id}` | Delete comment (author or post owner) |

### Likes

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/likes` | Like post or comment (`target_type`, `target_id`) |
| `DELETE` | `/likes` | Unlike (same JSON body) |
| `GET` | `/likes?target_type=&target_id=` | Who liked (`limit`, `offset`) |

`target_type`: `post` | `comment`

## Project structure

```
backend/
├── alembic/                 # Database migrations
├── app/
│   ├── main.py              # FastAPI app + CORS
│   ├── config.py            # Settings from environment
│   ├── database.py          # SQLAlchemy engine
│   ├── security.py          # Password hashing + JWT
│   ├── deps.py              # get_current_user
│   ├── routers/
│   │   ├── auth.py
│   │   ├── posts.py
│   │   ├── comments.py
│   │   └── likes.py
│   ├── services/
│   │   ├── cloudinary.py
│   │   ├── likes.py
│   │   └── access.py
│   ├── models/
│   └── schemas/
├── railway.toml             # Railway deploy config
├── Procfile
├── requirements.txt
└── .env.example
```

## Design decisions

- **JWT in httpOnly cookies** instead of localStorage — reduces XSS token theft risk; requires correct CORS + cookie flags in production.
- **Cloudinary** for post images and avatars — keeps the API stateless for file storage.
- **Polymorphic likes table** — one like model for posts and comments.
- **Private posts** — filtered at query time so only the author sees their private content.
- **Pagination** — offset/limit on posts and likes for scalable reads.

## Environment variables

| Variable | Description |
|----------|-------------|
| `FRONTEND_URL` | Primary frontend origin for CORS fallback |
| `CORS_ALLOWED_ORIGINS` | Comma-separated browser origins allowed by CORS |
| `DATABASE_URL` | PostgreSQL connection string |
| `JWT_SECRET` | Token signing secret |
| `COOKIE_SECURE` | `true` in production (HTTPS) |
| `COOKIE_SAMESITE` | `lax` locally; `none` for cross-domain deploys |
| `CLOUDINARY_*` | Image upload credentials |
| `MAX_UPLOAD_SIZE_MB` | Max upload size (default `5`) |

Railway injects `PORT` automatically — the start command binds to it.
