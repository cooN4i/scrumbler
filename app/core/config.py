from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Scrumbler"
    VERSION: str = "0.1.0"
    DEBUG: bool = True

    # Database
    # Default for local development: SQLite with async driver (aiosqlite)
    # For Docker / production: postgresql+asyncpg://user:password@localhost:5432/scrumbler
    DATABASE_URL: str = "sqlite+aiosqlite:///./scrumbler.db"

    # Security & JWT
    SECRET_KEY: str = "scrumbler-super-secret-key-change-in-production-2026-wca"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Cookie name for web interface
    AUTH_COOKIE_NAME: str = "scrumbler_token"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
