"""Application settings loaded from the environment or a .env file.

Every value can be overridden at runtime via environment variables so the
same image runs in development, staging, and production without recompiling.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the ANNEX backend."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "ANNEX Backend"
    version: str = "0.1.0"
    environment: str = Field(
        default="development",
        pattern="^(development|staging|production)$",
    )
    debug: bool = False
    api_prefix: str = "/api/v1"
    allowed_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
    ]

    # Logging
    log_level: str = Field(
        default="INFO",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
    )
    log_json: bool = False

    # Security
    security_headers_enabled: bool = True

    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60

    # Database — local compose default; override with the Supabase direct
    # connection string (with ?sslmode=require) for staging/production.
    database_url: str = "postgresql+psycopg://annex:annex@localhost:5432/annex"

    # Supabase (storage + project access)
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    storage_bucket: str = "annex-media"

    # Firebase Auth
    firebase_project_id: str = ""
    firebase_api_key: str = ""
    firebase_auth_domain: str = ""
    firebase_service_account_path: str = ""

    # Redis / Celery
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"
    
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str | None = None
    analysis_run_async: bool = True
    
    # Groq fallback (free tier) — used when the primary LLM is rate-limited
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    groq_vision_model: str = "llama-3.2-11b-vision-preview"


    exa_api_key: str = ""




@lru_cache
def get_settings() -> Settings:
    """Return the process-wide cached Settings instance (loaded once)."""
    return Settings()


