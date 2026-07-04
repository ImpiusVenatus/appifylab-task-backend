from fastapi import APIRouter

from app.database import check_database_connection
from app.routers import auth, comments, posts

router = APIRouter(prefix="/api/v1")

router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(posts.router, prefix="/posts", tags=["posts"])
router.include_router(comments.router, prefix="/posts", tags=["comments"])


@router.get("/health")
def health_check() -> dict:
    db_ok = check_database_connection()
    return {
        "status": "ok" if db_ok else "degraded",
        "database": "connected" if db_ok else "disconnected",
    }
