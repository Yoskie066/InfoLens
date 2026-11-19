
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application Configuration
    APP_NAME: str = "InfoLens"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # Database Configuration
    DATABASE_URL: str

    # JWT Configuration
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Email Configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    EMAIL_FROM: str
    FRONTEND_URL: str = "http://localhost:5173"

    # Tavily Search Configuration
    TAVILY_API_KEY: str

    # Environment File Configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
