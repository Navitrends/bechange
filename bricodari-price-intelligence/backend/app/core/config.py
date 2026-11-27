from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Bricodari Price Intelligence"
    app_env: str = "development"
    secret_key: str = "dev-secret"
    database_url: str = f"sqlite:///{ROOT_DIR / 'bricodari.db'}"
    redis_url: str = "redis://localhost:6379/0"

    woocommerce_url: str = "https://bricodari.tn"
    woocommerce_consumer_key: str = ""
    woocommerce_consumer_secret: str = ""

    # Sync automatique catalogue (heures)
    woo_sync_enabled: bool = True
    woo_sync_interval_hours: int = 6

    upload_dir: str = str(ROOT_DIR / "uploads")


@lru_cache
def get_settings() -> Settings:
    return Settings()
