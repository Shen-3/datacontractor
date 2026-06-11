from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://datacontractor:datacontractor@localhost:5432/datacontractor"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
