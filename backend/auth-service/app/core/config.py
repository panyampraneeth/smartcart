from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://smartcart:smartcart@localhost:5433/smartcart"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # App
    APP_NAME: str = "SmartCart Auth Service"
    DEBUG: bool = True

    class Config:
        env_file = ".env"


# Single instance used across the app
settings = Settings()
