"""Application settings loaded from environment variables (or a .env file)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application settings with safe local defaults."""

    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/fastapi_db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()