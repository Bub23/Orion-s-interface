"""
Core configuration settings
Pydantic v2 Settings
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # APP
    APP_NAME: str = "Sound Savage AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # DATABASE
    DATABASE_URL: str = "postgresql://user:password@localhost/sound_savage"
    
    # JWT
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # EXTERNAL APIs
    OPENAI_API_KEY: str = ""
    RUNWAY_API_KEY: str = ""
    HEYGEN_API_KEY: str = ""
    SYNTHESIA_API_KEY: str = ""
    TIKTOK_CLIENT_KEY: str = ""
    TIKTOK_CLIENT_SECRET: str = ""
    
    # REDIS
    REDIS_URL: str = "redis://localhost:6379"
    
    class Config:
        env_file = ".env"


settings = Settings()
