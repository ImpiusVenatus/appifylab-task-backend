from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    app_name: str = "AppifyLab API"
    debug: bool = False

    # Server
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Frontend (CORS)
    frontend_url: str = "http://localhost:3000"

    # NeonDB (PostgreSQL)
    database_url: str = "postgresql://user:password@host/dbname?sslmode=require"

    # Auth (used in later phases)
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # Cookie settings for JWT
    cookie_name: str = "access_token"
    cookie_secure: bool = False  # set True in production (HTTPS)
    cookie_httponly: bool = True
    cookie_samesite: str = "lax"  # "lax" | "strict" | "none"


@lru_cache
def get_settings() -> Settings:
    return Settings()
