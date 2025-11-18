# Phase 3: Python Subprocess Manager

## 🎯 Objective

Implement a robust Python subprocess manager that controls the Node.js validator's lifecycle, handles communication, monitors health, and provides automatic recovery.

**Estimated Time**: 60-75 minutes  
**Commit Message**: `feat: add Python subprocess manager for Node.js validator`

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│         Python Subprocess Manager                    │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │  Lifecycle Manager                          │    │
│  │  - start(): Launch Node.js process          │    │
│  │  - stop(): Graceful shutdown                │    │
│  │  - restart(): Stop + Start                  │    │
│  └────────────────────────────────────────────┘    │
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │  Health Monitor                             │    │
│  │  - HTTP health checks (GET /health)         │    │
│  │  - Process state monitoring                 │    │
│  │  - Auto-restart on failure                  │    │
│  └────────────────────────────────────────────┘    │
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │  Validation Client                          │    │
│  │  - HTTP POST to /validate                   │    │
│  │  - Timeout handling                         │    │
│  │  - Response parsing                         │    │
│  └────────────────────────────────────────────┘    │
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │  Log Streaming                              │    │
│  │  - Capture stdout/stderr                    │    │
│  │  - Forward to Python logger                 │    │
│  │  - Error detection                          │    │
│  └────────────────────────────────────────────┘    │
│                                                      │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │  Node.js Process  │
              │  (port 3001)      │
              └──────────────────┘
```

---

## 🔍 Design Decisions

### State Management

**Process States**:

```python
from enum import Enum

class ProcessState(Enum):
    """Subprocess lifecycle states"""
    STOPPED = "stopped"       # Not started yet
    STARTING = "starting"     # Launching, waiting for ready
    RUNNING = "running"       # Healthy and operational
    UNHEALTHY = "unhealthy"   # Running but failing health checks
    STOPPING = "stopping"     # Graceful shutdown in progress
    FAILED = "failed"         # Startup failed or crashed
```

**State Transitions**:

```
STOPPED ─start()─> STARTING ─health_ok─> RUNNING
   ▲                  │                      │
   │                  │                      │ health_fail
   │                  │                      ▼
   │                  │                  UNHEALTHY
   │                  │                      │
   │                  │ startup_fail         │ restart()
   │                  ▼                      │
   │               FAILED                    │
   │                  │                      │
   └──────────────────┴──────────────────────┘
```

### Async vs Sync

**Decision**: Fully async implementation

**Why?**

```python
# Blocking (BAD for FastAPI)
def start_subprocess():
    process = subprocess.Popen(["node", "server.js"])
    time.sleep(5)  # Blocks entire event loop!
    return process

# Non-blocking (GOOD for FastAPI)
async def start_subprocess():
    process = await asyncio.create_subprocess_exec("node", "server.js")
    await asyncio.sleep(0.1)  # Yields control
    return process
```

### Health Check Strategy

**Multi-layer health checks**:

1. **Process Check**: Is process still running?
2. **HTTP Check**: Does HTTP server respond?
3. **Performance Check**: Response time < threshold?
4. **Memory Check**: RAM usage < limit?

---

## 🛠️ Implementation Steps

### Step 1: Create Configuration Module

**File**: `services/mermaid_validator/config.py`

```python
"""
Configuration for Mermaid validator subprocess.

Loads settings from environment variables with sensible defaults.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class ValidatorConfig(BaseSettings):
    """
    Configuration for Mermaid validator subprocess.

    All settings can be overridden via environment variables with
    MERMAID_VALIDATOR_ prefix.

    Example:
        MERMAID_VALIDATOR_PORT=3002
        MERMAID_VALIDATOR_TIMEOUT=15
    """

    # Server configuration
    enabled: bool = True
    host: str = "localhost"
    port: int = 3001

    # Timeouts (seconds)
    startup_timeout: int = 30
    request_timeout: int = 10
    shutdown_timeout: int = 5
    health_check_timeout: int = 2

    # Retry configuration
    max_retries: int = 3
    retry_delay: int = 2

    # Health monitoring
    health_check_interval: int = 30
    max_consecutive_failures: int = 3

    # Performance limits
    max_memory_mb: int = 500
    max_cpu_percent: float = 80.0

    # Paths
    script_path: Optional[Path] = None
    log_level: str = "INFO"

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
```

---

### Step 2: Create Subprocess Manager

**File**: `services/mermaid_validator/subprocess_manager.py`

```python
"""
Subprocess manager for Node.js Mermaid validator.

Handles lifecycle management, health monitoring, and automatic recovery
of the Node.js validation server subprocess.
"""

import asyncio
import logging
import psutil
from pathlib import Path
from typing import Optional
from enum import Enum
import httpx

from .config import ValidatorConfig, get_config
from .exceptions import (
    SubprocessStartupError,
    SubprocessUnavailable,
    ValidationTimeout
)


logger = logging.getLogger(__name__)


class ProcessState(Enum):
    """Subprocess lifecycle states"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    UNHEALTHY = "unhealthy"
    STOPPING = "stopping"
    FAILED = "failed"


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

    def __init__(self, config: Optional[ValidatorConfig] = None):
        """
        Initialize subprocess manager.

        Args:
            config: Optional configuration override
        """
        self.config = config or get_config()
        self.process: Optional[asyncio.subprocess.Process] = None
        self.state = ProcessState.STOPPED
        self._log_task: Optional[asyncio.Task] = None
        self._health_task: Optional[asyncio.Task] = None
        self._consecutive_failures = 0

        logger.info(f"Initialized validator manager: {self.config.base_url}")

    async def __aenter__(self):
        """Async context manager entry"""
        if self.config.enabled:
            await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.stop()

    @property
    def is_running(self) -> bool:
        """Check if process is running"""
        return (
            self.process is not None and
            self.process.returncode is None and
            self.state in [ProcessState.RUNNING, ProcessState.STARTING, ProcessState.UNHEALTHY]
        )

    @property
    def is_healthy(self) -> bool:
        """Check if process is healthy"""
        return self.state == ProcessState.RUNNING

    async def start(self):
        """
        Start Node.js validator subprocess.

        Raises:
            SubprocessStartupError: If startup fails
        """
        if self.is_running:
            logger.warning("Subprocess already running")
            return

        logger.info("Starting Node.js validator subprocess...")
        self.state = ProcessState.STARTING

        try:
            # Start subprocess
            self.process = await asyncio.create_subprocess_exec(
                "node",
                str(self.config.script_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.config.script_path.parent),
                env={
                    **dict(os.environ),
                    "PORT": str(self.config.port),
                    "HOST": self.config.host,
                    "NODE_ENV": "production"
                }
            )

            logger.info(f"Subprocess started with PID: {self.process.pid}")

            # Start log streaming
            self._log_task = asyncio.create_task(self._stream_logs())

            # Wait for server to be ready
            await self._wait_for_ready()

            # Start health monitoring
            self._health_task = asyncio.create_task(self._monitor_health())

            self.state = ProcessState.RUNNING
            self._consecutive_failures = 0

            logger.info("✓ Validator subprocess started successfully")

        except Exception as e:
            self.state = ProcessState.FAILED
            logger.error(f"Failed to start subprocess: {e}", exc_info=True)
            await self._cleanup()
            raise SubprocessStartupError(f"Subprocess startup failed: {e}") from e

    async def stop(self):
        """
        Stop Node.js validator subprocess gracefully.
        """
        if not self.is_running:
            logger.debug("Subprocess not running, nothing to stop")
            return

        logger.info("Stopping Node.js validator subprocess...")
        self.state = ProcessState.STOPPING

        try:
            # Cancel monitoring tasks
            if self._health_task:
                self._health_task.cancel()
                try:
                    await self._health_task
                except asyncio.CancelledError:
                    pass

            if self._log_task:
                self._log_task.cancel()
                try:
                    await self._log_task
                except asyncio.CancelledError:
                    pass

            # Graceful shutdown
            if self.process:
                self.process.terminate()  # SIGTERM

                try:
                    await asyncio.wait_for(
                        self.process.wait(),
                        timeout=self.config.shutdown_timeout
                    )
                    logger.info("Subprocess terminated gracefully")
                except asyncio.TimeoutError:
                    logger.warning("Graceful shutdown timeout, forcing kill")
                    self.process.kill()  # SIGKILL
                    await self.process.wait()

            await self._cleanup()
            self.state = ProcessState.STOPPED
            logger.info("✓ Validator subprocess stopped")

        except Exception as e:
            logger.error(f"Error stopping subprocess: {e}", exc_info=True)
            await self._cleanup()
            self.state = ProcessState.FAILED

    async def restart(self):
        """
        Restart subprocess (stop + start).
        """
        logger.info("Restarting Node.js validator subprocess...")
        await self.stop()
        await asyncio.sleep(1)  # Brief pause
        await self.start()

    async def health_check(self) -> bool:
        """
        Perform health check on subprocess.

        Returns:
            True if healthy, False otherwise
        """
        if not self.is_running:
            return False

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.config.health_url,
                    timeout=self.config.health_check_timeout
                )
                return response.status_code == 200
        except Exception as e:
            logger.debug(f"Health check failed: {e}")
            return False

    def get_metrics(self) -> dict:
        """
        Get subprocess performance metrics.

        Returns:
            Dictionary with CPU, memory, and status metrics
        """
        if not self.is_running or not self.process:
            return {
                "state": self.state.value,
                "running": False
            }

        try:
            ps = psutil.Process(self.process.pid)

            return {
                "state": self.state.value,
                "running": True,
                "pid": self.process.pid,
                "cpu_percent": ps.cpu_percent(interval=0.1),
                "memory_mb": ps.memory_info().rss / 1024 / 1024,
                "num_threads": ps.num_threads(),
                "uptime_seconds": asyncio.get_event_loop().time() - ps.create_time(),
                "consecutive_failures": self._consecutive_failures
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.warning(f"Failed to get metrics: {e}")
            return {
                "state": self.state.value,
                "running": False,
                "error": str(e)
            }

    async def _wait_for_ready(self):
        """
        Wait for Node.js server to be ready (health check passes).

        Raises:
            SubprocessStartupError: If server doesn't become ready in time
        """
        logger.info("Waiting for validator server to be ready...")

        start_time = asyncio.get_event_loop().time()
        check_interval = 0.5  # seconds

        while True:
            # Check if process died
            if self.process.returncode is not None:
                raise SubprocessStartupError(
                    f"Process exited during startup with code {self.process.returncode}"
                )

            # Check timeout
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > self.config.startup_timeout:
                raise SubprocessStartupError(
                    f"Startup timeout ({self.config.startup_timeout}s)"
                )

            # Try health check
            if await self.health_check():
                logger.info(f"✓ Server ready after {elapsed:.1f}s")
                return

            # Wait before retry
            await asyncio.sleep(check_interval)

    async def _stream_logs(self):
        """
        Stream subprocess stdout/stderr to Python logger.
        """
        if not self.process:
            return

        async def stream_output(stream, level):
            """Stream single output stream"""
            try:
                async for line in stream:
                    text = line.decode().strip()
                    if text:
                        logger.log(level, f"[NodeJS] {text}")
            except Exception as e:
                logger.error(f"Log streaming error: {e}")

        # Stream both stdout and stderr concurrently
        await asyncio.gather(
            stream_output(self.process.stdout, logging.INFO),
            stream_output(self.process.stderr, logging.ERROR),
            return_exceptions=True
        )

    async def _monitor_health(self):
        """
        Background task to monitor subprocess health.

        Auto-restarts on repeated failures.
        """
        while self.is_running:
            try:
                await asyncio.sleep(self.config.health_check_interval)

                if not self.is_running:
                    break

                is_healthy = await self.health_check()

                if is_healthy:
                    if self.state == ProcessState.UNHEALTHY:
                        logger.info("Subprocess recovered")
                        self.state = ProcessState.RUNNING
                    self._consecutive_failures = 0
                else:
                    self._consecutive_failures += 1
                    logger.warning(
                        f"Health check failed "
                        f"({self._consecutive_failures}/{self.config.max_consecutive_failures})"
                    )

                    self.state = ProcessState.UNHEALTHY

                    # Auto-restart after max failures
                    if self._consecutive_failures >= self.config.max_consecutive_failures:
                        logger.error("Max consecutive failures reached, restarting...")
                        await self.restart()
                        break

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitoring error: {e}", exc_info=True)

    async def _cleanup(self):
        """Clean up resources"""
        self.process = None
        self._log_task = None
        self._health_task = None


# Add missing import
import os
```

---

### Step 3: Create Validation Client

**File**: `services/mermaid_validator/client.py`

```python
"""
HTTP client for Mermaid validator subprocess.

Provides high-level interface for validation requests.
"""

import logging
from typing import Dict, Any, Optional
import httpx

from .config import ValidatorConfig, get_config
from .exceptions import SubprocessUnavailable, ValidationTimeout


logger = logging.getLogger(__name__)


class MermaidValidatorClient:
    """
    HTTP client for Mermaid validation requests.

    This client communicates with the Node.js subprocess via HTTP.

    Usage:
        client = MermaidValidatorClient()
        result = await client.validate("graph TD\\nA-->B")
    """

    def __init__(
        self,
        config: Optional[ValidatorConfig] = None,
        http_client: Optional[httpx.AsyncClient] = None
    ):
        """
        Initialize validation client.

        Args:
            config: Optional configuration override
            http_client: Optional httpx client for testing
        """
        self.config = config or get_config()
        self._http_client = http_client
        self._owned_client = http_client is None

    async def __aenter__(self):
        """Async context manager entry"""
        if self._owned_client:
            self._http_client = httpx.AsyncClient(
                timeout=self.config.request_timeout
            )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self._owned_client and self._http_client:
            await self._http_client.aclose()

    async def validate(self, mermaid_code: str) -> Dict[str, Any]:
        """
        Validate Mermaid diagram code.

        Args:
            mermaid_code: Mermaid diagram code to validate

        Returns:
            Validation result dictionary:
                {
                    "valid": bool,
                    "code": str,
                    "diagram_type": str (if valid),
                    "errors": list (if invalid),
                    "timestamp": int,
                    "duration_ms": int
                }

        Raises:
            SubprocessUnavailable: If subprocess is not reachable
            ValidationTimeout: If validation times out
        """
        if not self._http_client:
            # Create temporary client if not in context
            async with httpx.AsyncClient(timeout=self.config.request_timeout) as client:
                return await self._do_validate(client, mermaid_code)

        return await self._do_validate(self._http_client, mermaid_code)

    async def _do_validate(
        self,
        client: httpx.AsyncClient,
        mermaid_code: str
    ) -> Dict[str, Any]:
        """
        Perform validation request.

        Args:
            client: HTTP client
            mermaid_code: Mermaid code to validate

        Returns:
            Validation result
        """
        try:
            response = await client.post(
                self.config.validate_url,
                json={"code": mermaid_code},
                timeout=self.config.request_timeout
            )

            response.raise_for_status()
            return response.json()

        except httpx.TimeoutException as e:
            logger.error(f"Validation timeout after {self.config.request_timeout}s")
            raise ValidationTimeout(
                f"Validation timeout after {self.config.request_timeout}s",
                timeout=self.config.request_timeout
            ) from e

        except httpx.ConnectError as e:
            logger.error(f"Cannot connect to validator: {e}")
            raise SubprocessUnavailable(
                f"Validator subprocess unavailable at {self.config.base_url}"
            ) from e

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during validation: {e}")
            # Still return a result, just mark as invalid
            return {
                "valid": False,
                "code": mermaid_code,
                "errors": [{
                    "message": f"HTTP {e.response.status_code}: {e.response.text}",
                    "type": "HTTPError"
                }],
                "timestamp": int(asyncio.get_event_loop().time() * 1000)
            }

        except Exception as e:
            logger.error(f"Unexpected validation error: {e}", exc_info=True)
            raise SubprocessUnavailable(
                f"Validation failed: {str(e)}"
            ) from e

    async def health_check(self) -> bool:
        """
        Check if validator is healthy.

        Returns:
            True if healthy, False otherwise
        """
        try:
            if not self._http_client:
                async with httpx.AsyncClient(timeout=2.0) as client:
                    response = await client.get(self.config.health_url)
            else:
                response = await self._http_client.get(
                    self.config.health_url,
                    timeout=2.0
                )

            return response.status_code == 200

        except Exception as e:
            logger.debug(f"Health check failed: {e}")
            return False


# Convenience function for simple use
async def validate_mermaid(code: str) -> Dict[str, Any]:
    """
    Standalone function to validate Mermaid code.

    Args:
        code: Mermaid diagram code

    Returns:
        Validation result

    Example:
        result = await validate_mermaid("graph TD\\nA-->B")
        if result["valid"]:
            print("Valid diagram!")
    """
    async with MermaidValidatorClient() as client:
        return await client.validate(code)


# Add missing import
import asyncio
```

---

### Step 4: Update Package **init**.py

**File**: `services/mermaid_validator/__init__.py`

```python
"""
Mermaid Validator Service

Node.js subprocess-based Mermaid diagram validation.

Components:
    - subprocess_manager: Lifecycle management for Node.js validator
    - client: HTTP client for validation requests
    - config: Configuration management
    - exceptions: Custom exception classes

Usage:
    # Simple validation
    from services.mermaid_validator import validate_mermaid

    result = await validate_mermaid("graph TD\\nA-->B")
    if result["valid"]:
        print("Valid diagram!")

    # With subprocess manager
    from services.mermaid_validator import MermaidSubprocessManager

    async with MermaidSubprocessManager() as manager:
        result = await manager.validate("graph TD\\nA-->B")
"""

from .exceptions import (
    MermaidValidatorError,
    SubprocessStartupError,
    SubprocessUnavailable,
    ValidationTimeout
)
from .config import ValidatorConfig, get_config, reset_config
from .subprocess_manager import MermaidSubprocessManager, ProcessState
from .client import MermaidValidatorClient, validate_mermaid

__version__ = "1.0.0"

__all__ = [
    # Exceptions
    "MermaidValidatorError",
    "SubprocessStartupError",
    "SubprocessUnavailable",
    "ValidationTimeout",

    # Configuration
    "ValidatorConfig",
    "get_config",
    "reset_config",

    # Subprocess management
    "MermaidSubprocessManager",
    "ProcessState",

    # Client
    "MermaidValidatorClient",
    "validate_mermaid",
]
```

---

### Step 5: Create Unit Tests

**File**: `tests/test_subprocess_manager.py`

```python
"""
Unit tests for subprocess manager.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from services.mermaid_validator.subprocess_manager import (
    MermaidSubprocessManager,
    ProcessState
)
from services.mermaid_validator.config import ValidatorConfig
from services.mermaid_validator.exceptions import (
    SubprocessStartupError,
    SubprocessUnavailable
)


@pytest.fixture
def test_config():
    """Test configuration with disabled validator"""
    return ValidatorConfig(
        enabled=False,
        port=3099,  # Different port for testing
        startup_timeout=5,
        health_check_interval=1
    )


@pytest.fixture
def mock_process():
    """Mock subprocess"""
    process = AsyncMock()
    process.pid = 12345
    process.returncode = None
    process.stdout = AsyncMock()
    process.stderr = AsyncMock()
    process.wait = AsyncMock()
    process.terminate = MagicMock()
    process.kill = MagicMock()
    return process


class TestSubprocessManager:
    """Test subprocess manager functionality"""

    @pytest.mark.asyncio
    async def test_initialization(self, test_config):
        """Test manager initialization"""
        manager = MermaidSubprocessManager(test_config)

        assert manager.config == test_config
        assert manager.state == ProcessState.STOPPED
        assert manager.process is None
        assert not manager.is_running
        assert not manager.is_healthy

    @pytest.mark.asyncio
    @patch('asyncio.create_subprocess_exec')
    @patch('httpx.AsyncClient')
    async def test_start_success(
        self,
        mock_http_client,
        mock_create_subprocess,
        test_config,
        mock_process
    ):
        """Test successful subprocess start"""
        # Mock subprocess creation
        mock_create_subprocess.return_value = mock_process

        # Mock health check success
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_http_client.return_value = mock_client_instance

        # Start manager
        manager = MermaidSubprocessManager(test_config)
        manager.config.enabled = True

        await manager.start()

        assert manager.state == ProcessState.RUNNING
        assert manager.is_running
        assert manager.process == mock_process

        # Cleanup
        await manager.stop()

    @pytest.mark.asyncio
    @patch('asyncio.create_subprocess_exec')
    async def test_start_failure(
        self,
        mock_create_subprocess,
        test_config
    ):
        """Test subprocess start failure"""
        # Mock subprocess creation failure
        mock_create_subprocess.side_effect = Exception("Failed to start")

        manager = MermaidSubprocessManager(test_config)
        manager.config.enabled = True

        with pytest.raises(SubprocessStartupError):
            await manager.start()

        assert manager.state == ProcessState.FAILED
        assert not manager.is_running

    @pytest.mark.asyncio
    async def test_stop_not_running(self, test_config):
        """Test stopping when not running"""
        manager = MermaidSubprocessManager(test_config)

        # Should not raise error
        await manager.stop()

        assert manager.state == ProcessState.STOPPED

    @pytest.mark.asyncio
    @patch('asyncio.create_subprocess_exec')
    async def test_graceful_stop(
        self,
        mock_create_subprocess,
        test_config,
        mock_process
    ):
        """Test graceful shutdown"""
        mock_create_subprocess.return_value = mock_process

        manager = MermaidSubprocessManager(test_config)
        manager.process = mock_process
        manager.state = ProcessState.RUNNING

        await manager.stop()

        # Should call terminate (SIGTERM)
        mock_process.terminate.assert_called_once()
        assert manager.state == ProcessState.STOPPED

    @pytest.mark.asyncio
    async def test_forced_stop(self, test_config, mock_process):
        """Test forced shutdown after timeout"""
        # Mock wait timeout
        async def wait_timeout():
            await asyncio.sleep(10)  # Longer than shutdown_timeout

        mock_process.wait = wait_timeout

        manager = MermaidSubprocessManager(test_config)
        manager.process = mock_process
        manager.state = ProcessState.RUNNING

        await manager.stop()

        # Should call kill after timeout
        mock_process.kill.assert_called_once()

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_health_check_success(
        self,
        mock_http_client,
        test_config,
        mock_process
    ):
        """Test successful health check"""
        # Mock HTTP response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_http_client.return_value = mock_client_instance

        manager = MermaidSubprocessManager(test_config)
        manager.process = mock_process
        manager.state = ProcessState.RUNNING

        is_healthy = await manager.health_check()

        assert is_healthy is True

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_health_check_failure(
        self,
        mock_http_client,
        test_config,
        mock_process
    ):
        """Test failed health check"""
        # Mock HTTP error
        mock_client_instance = AsyncMock()
        mock_client_instance.get.side_effect = httpx.ConnectError("Connection failed")
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_http_client.return_value = mock_client_instance

        manager = MermaidSubprocessManager(test_config)
        manager.process = mock_process
        manager.state = ProcessState.RUNNING

        is_healthy = await manager.health_check()

        assert is_healthy is False

    @pytest.mark.asyncio
    async def test_metrics_not_running(self, test_config):
        """Test metrics when process not running"""
        manager = MermaidSubprocessManager(test_config)

        metrics = manager.get_metrics()

        assert metrics["running"] is False
        assert metrics["state"] == ProcessState.STOPPED.value

    @pytest.mark.asyncio
    @patch('psutil.Process')
    async def test_metrics_running(
        self,
        mock_psutil_process,
        test_config,
        mock_process
    ):
        """Test metrics when process running"""
        # Mock psutil
        mock_ps = MagicMock()
        mock_ps.cpu_percent.return_value = 10.5
        mock_ps.memory_info.return_value.rss = 50 * 1024 * 1024  # 50 MB
        mock_ps.num_threads.return_value = 5
        mock_ps.create_time.return_value = asyncio.get_event_loop().time() - 60
        mock_psutil_process.return_value = mock_ps

        manager = MermaidSubprocessManager(test_config)
        manager.process = mock_process
        manager.state = ProcessState.RUNNING

        metrics = manager.get_metrics()

        assert metrics["running"] is True
        assert metrics["pid"] == 12345
        assert metrics["cpu_percent"] == 10.5
        assert metrics["memory_mb"] == 50.0
        assert metrics["num_threads"] == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

### Step 6: Create Integration Test

**File**: `tests/test_validator_client.py`

```python
"""
Integration tests for validator client.
"""

import pytest
from unittest.mock import AsyncMock, patch
import httpx

from services.mermaid_validator.client import (
    MermaidValidatorClient,
    validate_mermaid
)
from services.mermaid_validator.config import ValidatorConfig
from services.mermaid_validator.exceptions import (
    SubprocessUnavailable,
    ValidationTimeout
)


@pytest.fixture
def test_config():
    """Test configuration"""
    return ValidatorConfig(
        port=3099,
        request_timeout=5
    )


class TestValidatorClient:
    """Test validation client"""

    @pytest.mark.asyncio
    async def test_validate_success(self, test_config):
        """Test successful validation"""
        # Mock HTTP response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "valid": True,
            "code": "graph TD\nA-->B",
            "diagram_type": "flowchart",
            "timestamp": 1699999999
        }

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        client = MermaidValidatorClient(test_config, mock_client)
        result = await client.validate("graph TD\nA-->B")

        assert result["valid"] is True
        assert result["diagram_type"] == "flowchart"

    @pytest.mark.asyncio
    async def test_validate_invalid(self, test_config):
        """Test validation of invalid diagram"""
        # Mock HTTP response for invalid diagram
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "valid": False,
            "code": "graph TD\nA--INVALID-->B",
            "errors": [
                {
                    "message": "Invalid arrow syntax",
                    "type": "ValidationError",
                    "line": 2
                }
            ],
            "timestamp": 1699999999
        }

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        client = MermaidValidatorClient(test_config, mock_client)
        result = await client.validate("graph TD\nA--INVALID-->B")

        assert result["valid"] is False
        assert len(result["errors"]) > 0
        assert result["errors"][0]["message"] == "Invalid arrow syntax"

    @pytest.mark.asyncio
    async def test_validate_timeout(self, test_config):
        """Test validation timeout"""
        # Mock timeout
        mock_client = AsyncMock()
        mock_client.post.side_effect = httpx.TimeoutException("Timeout")

        client = MermaidValidatorClient(test_config, mock_client)

        with pytest.raises(ValidationTimeout):
            await client.validate("graph TD\nA-->B")

    @pytest.mark.asyncio
    async def test_validate_connection_error(self, test_config):
        """Test connection error"""
        # Mock connection error
        mock_client = AsyncMock()
        mock_client.post.side_effect = httpx.ConnectError("Cannot connect")

        client = MermaidValidatorClient(test_config, mock_client)

        with pytest.raises(SubprocessUnavailable):
            await client.validate("graph TD\nA-->B")

    @pytest.mark.asyncio
    async def test_health_check_success(self, test_config):
        """Test successful health check"""
        # Mock HTTP response
        mock_response = AsyncMock()
        mock_response.status_code = 200

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        client = MermaidValidatorClient(test_config, mock_client)
        is_healthy = await client.health_check()

        assert is_healthy is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self, test_config):
        """Test failed health check"""
        # Mock HTTP error
        mock_client = AsyncMock()
        mock_client.get.side_effect = httpx.ConnectError("Connection failed")

        client = MermaidValidatorClient(test_config, mock_client)
        is_healthy = await client.health_check()

        assert is_healthy is False

    @pytest.mark.asyncio
    @patch('services.mermaid_validator.client.MermaidValidatorClient')
    async def test_convenience_function(self, mock_client_class):
        """Test standalone validate_mermaid function"""
        # Mock client
        mock_client = AsyncMock()
        mock_client.validate.return_value = {"valid": True}
        mock_client.__aenter__.return_value = mock_client
        mock_client_class.return_value = mock_client

        result = await validate_mermaid("graph TD\nA-->B")

        assert result["valid"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

## ✅ Verification Checklist

Before proceeding to Phase 4, ensure:

- [ ] `config.py` created with ValidatorConfig
- [ ] `subprocess_manager.py` created with full lifecycle management
- [ ] `client.py` created with HTTP validation interface
- [ ] `__init__.py` updated with exports
- [ ] Unit tests created and passing
- [ ] Integration tests created and passing
- [ ] All imports resolved
- [ ] Type hints are correct
- [ ] Logging implemented throughout
- [ ] Error handling comprehensive

---

## 🎯 Commit Time!

```powershell
# Navigate to ba_copilot_ai root
cd d:\Do_an_tot_nghiep\ba_copilot_ai

# Stage changes
git add services/mermaid_validator/
git add tests/test_subprocess_manager.py
git add tests/test_validator_client.py

# Commit
git commit -m "feat: add Python subprocess manager for Node.js validator

- Implement MermaidSubprocessManager with lifecycle management
- Add ValidatorConfig for centralized configuration
- Create MermaidValidatorClient for HTTP communication
- Implement health monitoring and auto-restart
- Add process metrics with psutil
- Create comprehensive unit and integration tests

Features:
  - Async subprocess management with asyncio
  - HTTP-based validation requests
  - Automatic health monitoring every 30s
  - Auto-restart on repeated failures (3 strikes)
  - Process metrics (CPU, memory, uptime)
  - Log streaming from Node.js to Python
  - Graceful shutdown with timeout
  - Context manager support

Components:
  - config.py: Configuration management
  - subprocess_manager.py: Process lifecycle
  - client.py: HTTP client for validation
  - __init__.py: Package exports

Tests:
  - test_subprocess_manager.py: Manager unit tests
  - test_validator_client.py: Client integration tests

Refs: #OPS-317"
```

---

## 🐛 Troubleshooting

### Issue: Process won't start

**Symptom**:

```
SubprocessStartupError: Subprocess startup failed
```

**Debug**:

```python
# Add debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check Node.js available
import subprocess
subprocess.run(["node", "--version"], check=True)

# Check script exists
from pathlib import Path
script = Path("services/mermaid_validator/nodejs/server.js")
print(f"Script exists: {script.exists()}")
```

### Issue: Health checks always fail

**Symptom**:

```
Health check failed (1/3)
```

**Debug**:

```python
# Test health endpoint manually
import httpx
import asyncio

async def test():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:3001/health")
        print(response.status_code)
        print(response.json())

asyncio.run(test())
```

### Issue: Process becomes zombie

**Symptom**:
Process ID exists but not responding

**Solution**:

```python
# Force kill if needed
import psutil

def kill_zombie(pid):
    try:
        process = psutil.Process(pid)
        process.kill()  # SIGKILL
    except psutil.NoSuchProcess:
        pass
```

---

## 📚 Additional Resources

- [asyncio Subprocess](https://docs.python.org/3/library/asyncio-subprocess.html)
- [psutil Process Management](https://psutil.readthedocs.io/en/latest/#processes)
- [httpx Async Client](https://www.python-httpx.org/async/)
- [Python Context Managers](https://docs.python.org/3/library/contextlib.html)

---

**Next Phase**: [04_DOCKER_CONFIGURATION.md](./04_DOCKER_CONFIGURATION.md) →

---

**Phase 3 Complete** ✅  
**Est. Completion Time**: 60-75 minutes  
**Commit**: `feat: add Python subprocess manager for Node.js validator`
