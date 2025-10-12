"""
Configuration settings for BA Copilot AI Services.
"""

from typing import Optional, List
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pydantic import field_validator

# Resolve the project root .env regardless of current working directory
# This file lives at src/core/config.py, so project root is two levels up
ENV_PATH = str(Path(__file__).resolve().parents[2] / ".env")


class Settings(BaseSettings):
    """Application settings."""
    # Pydantic v2 settings configuration
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra='ignore',  # ignore unspecified env vars to avoid validation errors
    )
    
    # Basic app settings
    app_name: str = "BA Copilot AI Services"
    environment: str = "development"
    debug: bool = True
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database settings
    # Default points to docker network service names; overridden by env DATABASE_URL
    database_url: str = "postgresql://postgres:postgres123@postgres:5432/bacopilot_db"
    database_echo: bool = False  # Set to True to log SQL queries
    
    # Redis settings
    redis_url: str = "redis://redis:6379/0"
    
    # JWT settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS settings
    allowed_origins: List[str] = ["*"]
    
    @field_validator("allowed_origins", mode="before")
    @classmethod
    def _parse_allowed_origins(cls, v):
        if v is None or v == "":
            return ["*"]
        if isinstance(v, str):
            s = v.strip()
            if s.startswith("[") and s.endswith("]"):
                return v
            return [item.strip() for item in s.split(',') if item.strip()]
        return v
    
    # LLM API settings
    google_ai_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    # OpenRouter (OpenAI-compatible) settings
    openrouter_ai_api_key: Optional[str] = None
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
    
    # v2: model_config replaces inner Config

# Create global settings instance
settings = Settings()