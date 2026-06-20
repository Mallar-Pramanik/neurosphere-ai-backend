"""
Configuration settings for NeuroSphere AI Backend
"""

from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings"""

    # API Settings
    APP_NAME: str = "NeuroSphere AI Backend"
    APP_VERSION: str = "1.0.0"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    # Database Settings
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./neurosphere_ai.db"
    )
    # For PostgreSQL, use: postgresql://user:password@localhost/dbname
    # For MySQL, use: mysql://user:password@localhost/dbname


# CORS Settings
ALLOWED_ORIGINS: List[str] = [
    "*"
]

# JWT Settings
SECRET_KEY: str = os.getenv(
    "SECRET_KEY",
    "your-super-secret-key-change-this-in-production"
)
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

# Odysseus AI Settings
ODYSSEUS_MODEL_PATH: str = os.getenv(
    "ODYSSEUS_MODEL_PATH",
    "./models/odysseus_ai"
)
ODYSSEUS_MAX_TOKENS: int = int(os.getenv("ODYSSEUS_MAX_TOKENS", "2048"))
ODYSSEUS_TEMPERATURE: float = float(
    os.getenv("ODYSSEUS_TEMPERATURE", "0.7"))
ODYSSEUS_TOP_P: float = float(os.getenv("ODYSSEUS_TOP_P", "0.9"))

# Google API Settings
GOOGLE_CREDENTIALS_PATH: str = os.getenv(
    "GOOGLE_CREDENTIALS_PATH",
    "./credentials/google-credentials.json"
)
GOOGLE_PROJECT_ID: str = os.getenv("GOOGLE_PROJECT_ID", "")
GOOGLE_GMAIL_SCOPES: List[str] = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send"
]
GOOGLE_DRIVE_SCOPES: List[str] = [
    "https://www.googleapis.com/auth/drive.readonly"
]
GOOGLE_NLP_SCOPES: List[str] = [
    "https://www.googleapis.com/auth/cloud-platform"
]

# Logging Settings
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE: str = os.getenv("LOG_FILE", "./logs/neurosphere_ai.log")

# Feature Flags
ENABLE_ODYSSEUS_AI: bool = os.getenv(
    "ENABLE_ODYSSEUS_AI", "True").lower() == "true"
ENABLE_GOOGLE_APIS: bool = os.getenv(
    "ENABLE_GOOGLE_APIS", "True").lower() == "true"
ENABLE_FILE_PROCESSING: bool = os.getenv(
    "ENABLE_FILE_PROCESSING", "True").lower() == "true"

# Rate Limiting
RATE_LIMIT_ENABLED: bool = os.getenv(
    "RATE_LIMIT_ENABLED", "True").lower() == "true"
RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
RATE_LIMIT_PERIOD: int = int(
    os.getenv("RATE_LIMIT_PERIOD", "60"))  # seconds

# File Upload Settings
MAX_UPLOAD_SIZE: int = int(
    os.getenv("MAX_UPLOAD_SIZE", "10485760"))  # 10MB in bytes
ALLOWED_FILE_TYPES: List[str] = [
    "text/plain",
    "application/pdf",
    "application/json",
    "text/csv",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/markdown"
]

# Cache Settings
ENABLE_CACHE: bool = os.getenv("ENABLE_CACHE", "True").lower() == "true"
CACHE_EXPIRATION: int = int(
    os.getenv("CACHE_EXPIRATION", "3600"))  # 1 hour

# Email Settings
SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")


class Config:
    env_file = ".env"
    case_sensitive = True


# Create settings instance
settings = Settings()

# Log settings on startup


def log_settings():
    """Log important settings (without sensitive data)"""
    import logging
    logger = logging.getLogger(__name__)

    logger.info(f"App Name: {settings.APP_NAME}")
    logger.info(f"Version: {settings.APP_VERSION}")
    logger.info(f"Debug Mode: {settings.DEBUG}")
    logger.info(
        f"Database: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'SQLite'}")
    logger.info(f"Odysseus AI Enabled: {settings.ENABLE_ODYSSEUS_AI}")
    logger.info(f"Google APIs Enabled: {settings.ENABLE_GOOGLE_APIS}")
    logger.info(f"Rate Limiting Enabled: {settings.RATE_LIMIT_ENABLED}")
