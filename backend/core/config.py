"""
Configuration management using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    
    # Gemini API
    GEMINI_API_KEY: str = ""
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/guardrails_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # GitHub
    GITHUB_APP_ID: str = ""
    GITHUB_APP_PRIVATE_KEY_PATH: str = "./github-app-private-key.pem"
    GITHUB_WEBHOOK_SECRET: str = ""
    
    # Security
    SECRET_KEY: str = "change-me-in-production"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Data Residency
    DATA_RESIDENCY_REGION: str = "us-east-1"
    ENABLE_CODE_RETENTION: bool = False
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/guardrails.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
