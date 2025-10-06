"""
Configuration settings for BA Copilot AI Services.
"""

from typing import Optional, List
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

# Resolve the project root .env regardless of current working directory
# This file lives at src/core/config.py, so project root is two levels up
ENV_PATH = str(Path(__file__).resolve().parents[2] / ".env")


class Settings(BaseSettings):
    """Application settings."""
    
    # Basic app settings
    app_name: str = "BA Copilot AI Services"
    environment: str = "development"
    debug: bool = True
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database settings
    database_url: str = "postgresql://bacopilot_user:dev_password@localhost:5432/bacopilot"
    database_echo: bool = False  # Set to True to log SQL queries
    
    # Redis settings
    redis_url: str = "redis://localhost:6379/0"
    
    # JWT settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS settings
    allowed_origins: List[str] = ["*"]
    
    # LLM API settings
    google_ai_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    # OpenRouter (OpenAI-compatible) settings
    openrouter_api_key: Optional[str] = None
    openrouter_model: Optional[str] = "deepseek/deepseek-v3.1:free"
    openrouter_referer: Optional[str] = None  # for OpenRouter rankings (optional)
    openrouter_title: Optional[str] = None    # for OpenRouter rankings (optional)
    
    # File storage settings
    upload_directory: str = "./uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    # Logging settings
    log_level: str = "INFO"
    
    # Mock data settings
    mock_data_enabled: bool = True
    
    class Config:
        env_file = ENV_PATH  # Resolve to the project root .env
        env_file_encoding = "utf-8"
        case_sensitive = False

# Create global settings instance
settings = Settings()