"""
Subprocess manager for Node.js Mermaid validator.

Handles lifecycle management, health monitoring, and automatic recovery
of the Node.js validation server subprocess.
"""
import asyncio
import logging
# import psutil
# from pathlib import Path
from typing import Optional
from enum import Enum
# import httpx

from .config import ValidatorConfig, get_config
# from .exceptions import (
#     SubprocessStartupError,
#     SubprocessUnavailable,
#     ValidationTimeout
# )

logger = logging.getLogger(__name__)

class SubprocessState(Enum):
    """Subprocess lifecycle states"""
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"
    UNHEALTHY = "unhealthy"

class MermaidSubprocessManager:
    """
    Manages Node.js Mermaid validator subprocess.

    Responsibilities:
        - Start/stop Node.js server process
        - Monitor process health
        - Auto-restart on failure
        - Stream logs to Python logger
        - Provide validation interface

    Usage:
        async with MermaidSubprocessManager() as manager:
            result = await manager.validate("graph TD\\nA-->B")
    """

    def __init__(self, config: ValidatorConfig) -> None:
        """
        Initialize subprocess manager.

        Args:
            config: Optional configuration override
        """
        self.config: ValidatorConfig = config
        self.state = SubprocessState.STOPPED
        self.process: Optional[asyncio.subprocess.Process] = None

    async def start(self):
        pass

    @property
    def is_running(self) -> bool:
        """Check if process is running"""
        return (
            self.process is not None and
            self.process.returncode is None and
            self.state in [SubprocessState.RUNNING, SubprocessState.STARTING, SubprocessState.UNHEALTHY]
        )

    async def __aenter__(self):
        """Async context manager entry"""
        if self.config.enabled:
            await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.stop()

    async def stop(self):
        
        pass
