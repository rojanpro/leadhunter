from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "production"
    app_secret_key: str = Field(default="change-me")
    dashboard_admin_email: str = "admin@example.com"
    dashboard_admin_password: str = "change-me-now"
    cors_origins: str = "http://localhost:3000"
    api_rate_limit: str = "120/minute"

    database_url: str = "postgresql+psycopg://lead_hunter:lead_hunter@postgres:5432/lead_hunter"
    redis_url: str = "redis://redis:6379/0"
    celery_task_always_eager: bool = False

    google_places_api_key: str = ""
    google_oauth_client_id: str = ""
    google_sheets_credentials_json: str = ""
    google_sheet_id: str = ""

    evolution_base_url: str = ""
    evolution_api_key: str = ""
    evolution_instance_name: str = ""
    evolution_webhook_secret: str = ""

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_use_tls: bool = True

    lead_search_interval_minutes: int = 15
    max_places_per_run: int = 50
    max_whatsapp_per_run: int = 5
    max_whatsapp_per_day: int = 30
    max_email_per_day: int = 30
    message_delay_seconds: int = 90

    @field_validator("database_url")
    @classmethod
    def convert_postgres_url(cls, value: str) -> str:
        import os
        # Check alternative environment variables that platforms like Railway inject
        alternative_keys = ["DATABASE_PRIVATE_URL", "DATABASE_PUBLIC_URL", "POSTGRES_URL", "PGURL"]
        for key in alternative_keys:
            alt_val = os.environ.get(key)
            if alt_val:
                value = alt_val
                break
                
        # Check if individual connection components exist and build the URL dynamically
        pg_user = os.environ.get("PGUSER") or os.environ.get("POSTGRES_USER")
        pg_password = os.environ.get("PGPASSWORD") or os.environ.get("POSTGRES_PASSWORD")
        pg_host = os.environ.get("PGHOST") or os.environ.get("POSTGRES_HOST")
        pg_port = os.environ.get("PGPORT") or os.environ.get("POSTGRES_PORT") or "5432"
        pg_db = os.environ.get("PGDATABASE") or os.environ.get("POSTGRES_DB")
        
        if pg_user and pg_password and pg_host and pg_db:
            value = f"postgresql+psycopg://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"

        if value.startswith("postgresql://"):
            value = value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value

    @field_validator("cors_origins")
    @classmethod
    def normalize_origins(cls, value: str) -> str:
        return value.strip()

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
