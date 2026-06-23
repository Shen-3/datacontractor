import warnings

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://datacontractor:datacontractor@localhost:5432/datacontractor"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_LOG_LEVEL: str = "INFO"
    APP_LOG_FORMAT: str = "text"  # "text" | "json"

    # Database pool
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE: int = 3600

    # Security
    API_KEY: str = ""  # empty = auth disabled (development)
    ALLOWED_DATA_DIR: str = "/app/data"
    MAX_REQUEST_SIZE_MB: int = 10

    # CORS
    CORS_ORIGINS: str = "http://localhost:8501"

    # Rate limiting
    API_RATE_LIMIT: int = 60  # requests per minute per IP

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @field_validator("APP_ENV")
    @classmethod
    def validate_env(cls, v: str) -> str:
        allowed = {"development", "staging", "production"}
        if v.lower() not in allowed:
            raise ValueError(f"APP_ENV must be one of {allowed}, got '{v}'")
        return v.lower()

    @field_validator("APP_DEBUG")
    @classmethod
    def warn_debug_production(cls, v: bool, info) -> bool:
        if v and info.data.get("APP_ENV") == "production":
            warnings.warn("APP_DEBUG=True in production environment!")
        return v


settings = Settings()
