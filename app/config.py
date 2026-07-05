from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    app_name: str = "Buddy Script"
    debug: bool = False

    # Server
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Frontend primary origin (used for CORS when CORS_ALLOWED_ORIGINS is empty)
    frontend_url: str = "http://localhost:3000"

    # Comma-separated list of allowed browser origins for CORS, e.g.
    # http://localhost:3000,https://your-app.vercel.app
    cors_allowed_origins: str = ""

    # NeonDB (PostgreSQL)
    database_url: str = "postgresql://user:password@host/dbname?sslmode=require"

    # Auth
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # Cookie settings for JWT
    cookie_name: str = "access_token"
    cookie_secure: bool = False  # set True in production (HTTPS)
    cookie_httponly: bool = True
    cookie_samesite: str = "lax"  # use "none" with COOKIE_SECURE=true for cross-origin deploys

    # Cloudinary (image uploads)
    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""
    cloudinary_folder: str = "appifylab/posts"
    max_upload_size_mb: int = 5

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if isinstance(value, str) and value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql://", 1)
        return value

    @property
    def cors_origins(self) -> list[str]:
        if self.cors_allowed_origins.strip():
            return [
                origin.strip().rstrip("/")
                for origin in self.cors_allowed_origins.split(",")
                if origin.strip()
            ]
        return [self.frontend_url.rstrip("/")]


@lru_cache
def get_settings() -> Settings:
    return Settings()
