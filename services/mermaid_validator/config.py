"""
Configuration for Mermaid validator subprocess.

Loads settings from environment variables with sensible defaults.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv


load_dotenv()  # Load environment variables from .env

class ValidatorConfig(BaseSettings):
    """
    Configuration for Mermaid validator subprocess.

    All settings can be overridden via environment variables with
    MERMAID_VALIDATOR_ prefix.
    """
    enabled: bool = os.getenv("MERMAID_VALIDATOR_ENABLED", "true").lower() == "true"
    host: str = os.getenv("MERMAID_VALIDATOR_HOST", "localhost")
    port: int = int(os.getenv("MERMAID_VALIDATOR_PORT", 51234))

    # Timeouts (seconds)
    startup_timeout: int = int(os.getenv("MERMAID_VALIDATOR_STARTUP_TIMEOUT", 30))
    request_timeout: int = int(os.getenv("MERMAID_VALIDATOR_TIMEOUT", 10))
    shutdown_timeout: int = int(os.getenv("MERMAID_VALIDATOR_SHUTDOWN_TIMEOUT", 5))
    health_check_timeout: int = int(os.getenv("MERMAID_VALIDATOR_HEALTH_CHECK_TIMEOUT", 2))

    # Retry configuration
    max_retries: int = int(os.getenv("MERMAID_VALIDATOR_MAX_RETRIES", 3))
    retry_delay: int = int(os.getenv("MERMAID_VALIDATOR_RETRY_DELAY", 2))

    # Health monitoring
    health_check_interval: int = int(os.getenv("MERMAID_VALIDATOR_HEALTH_CHECK_INTERVAL", 30))
    max_consecutive_failures: int = int(os.getenv("MERMAID_VALIDATOR_MAX_CONSECUTIVE_FAILURES", 3))

    # Performance limits
    max_memory_mb: int = int(os.getenv("MERMAID_VALIDATOR_MAX_MEMORY_MB", 500))
    max_cpu_percent: float = float(os.getenv("MERMAID_VALIDATOR_MAX_CPU_PERCENT", 80.0))

    # Paths
    script_path: Optional[Path] = None
    log_level: str = os.getenv("MERMAID_VALIDATOR_LOG_LEVEL", "INFO")

    class Config:
        env_prefix = "MERMAID_VALIDATOR_"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Auto-detect script path if not provided
        if self.script_path is None:
            base_dir = Path(__file__).parent
            self.script_path = base_dir / "nodejs" / "server.js"

        # Validate script exists
        if not self.script_path.exists():
            raise FileNotFoundError(
                f"Validator script not found: {self.script_path}"
            )

    @property
    def base_url(self) -> str:
        """Get base URL for HTTP requests"""
        return f"http://{self.host}:{self.port}"

    @property
    def health_url(self) -> str:
        """Get health check URL"""
        return f"{self.base_url}/health"

    @property
    def validate_url(self) -> str:
        """Get validation endpoint URL"""
        return f"{self.base_url}/validate"


# Global config instance
_config: Optional[ValidatorConfig] = None


def get_config() -> ValidatorConfig:
    """
    Get or create validator configuration.

    Returns:
        ValidatorConfig instance
    """
    global _config
    if _config is None:
        _config = ValidatorConfig()
    return _config


def reset_config():
    """Reset configuration (useful for testing)"""
    global _config
    _config = None