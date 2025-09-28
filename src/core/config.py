"""
Configuration settings for BA Copilot AI Services.
"""

try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for older pydantic versions
    from pydantic import BaseSettings

from typing import Optional
import os

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
    allowed_origins: list[str] = ["*"]
    
    # LLM API settings
    openai_api_key: Optional[str] = None
    claude_api_key: Optional[str] = None
    
    # File storage settings
    upload_directory: str = "./uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    # Logging settings
    log_level: str = "INFO"
    
    # Mock data settings
    mock_data_enabled: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()