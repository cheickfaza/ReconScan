"""
Configuration de l'application ReconScan API
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuration settings"""
    
    APP_NAME: str = "ReconScan API"
    APP_VERSION: str = "4.0.0"
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./reconscan.db"
    
    # Scanner settings
    DEFAULT_TIMEOUT: int = 10
    MAX_CONCURRENT: int = 10
    MAX_RESULTS: int = 100
    
    # CORS
    CORS_ORIGINS: list = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["*"]
    CORS_ALLOW_HEADERS: list = ["*"]
    
    # HaveIBeenPwned API (optional)
    HIBP_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()