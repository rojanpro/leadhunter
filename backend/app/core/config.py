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
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
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
