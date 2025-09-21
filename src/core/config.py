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
    
    # CORS settings
    allowed_origins: list[str] = ["*"]
    
    # Mock data settings
    mock_data_enabled: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()