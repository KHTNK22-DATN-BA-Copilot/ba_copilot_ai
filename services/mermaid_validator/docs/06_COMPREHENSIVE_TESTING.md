# Phase 6: Comprehensive Testing

## 🎯 Objective

Create comprehensive test suite covering unit tests, integration tests, performance tests, and end-to-end tests to ensure 90%+ coverage and production readiness.

**Estimated Time**: 90-120 minutes  
**Commit Message**: `test: add comprehensive tests for validation system`

---

## 🧪 Testing Strategy

### Test Pyramid

```
         ┌─────────────┐
         │   E2E (5%)  │  Full workflow with real subprocess
         ├─────────────┤
         │Integration  │  Multiple components working together
         │   (20%)     │
         ├─────────────┤
         │    Unit     │  Individual functions and classes
         │   (75%)     │
         └─────────────┘
```

### Coverage Targets

| Component              | Target | Focus Areas                            |
| ---------------------- | ------ | -------------------------------------- |
| **Subprocess Manager** | 95%+   | Lifecycle, health checks, errors       |
| **Validator Client**   | 90%+   | HTTP communication, timeouts           |
| **Workflow Nodes**     | 90%+   | Validation, fix logic, edge conditions |
| **Config**             | 80%+   | Environment parsing, defaults          |
| **Overall**            | 90%+   | Critical paths covered                 |

---

## 🛠️ Implementation Steps

### Step 1: Configure pytest

**File**: `ba_copilot_ai/pytest.ini`

```ini
[pytest]
# Test discovery
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Async support
asyncio_mode = auto

# Coverage
addopts =
    --verbose
    --strict-markers
    --cov=services.mermaid_validator
    --cov=workflows
    --cov-report=html
    --cov-report=term-missing
    --cov-report=xml
    --cov-fail-under=90
    -p no:warnings

# Markers
markers =
    unit: Unit tests (fast, no external dependencies)
    integration: Integration tests (multiple components)
    e2e: End-to-end tests (full stack)
    slow: Slow tests (> 1 second)
    subprocess: Tests requiring real subprocess

# Timeout
timeout = 30
timeout_method = thread

# Logging
log_cli = true
log_cli_level = INFO
log_cli_format = %(asctime)s [%(levelname)8s] %(message)s
log_cli_date_format = %Y-%m-%d %H:%M:%S
```

---

### Step 2: Unit Tests - Config

**File**: `tests/unit/test_config.py`

```python
"""
Unit tests for validator configuration.
"""

import pytest
import os
from pathlib import Path

from services.mermaid_validator.config import ValidatorConfig, get_config, reset_config


@pytest.mark.unit
class TestValidatorConfig:
    """Test configuration management"""

    def setup_method(self):
        """Reset config before each test"""
        reset_config()
        # Clear environment
        for key in list(os.environ.keys()):
            if key.startswith("MERMAID_VALIDATOR_"):
                del os.environ[key]

    def test_default_values(self):
        """Test default configuration values"""
        config = ValidatorConfig()

        assert config.enabled is True
        assert config.host == "localhost"
        assert config.port == 3001
        assert config.startup_timeout == 30
        assert config.request_timeout == 10
        assert config.max_retries == 3

    def test_env_override(self):
        """Test environment variable override"""
        os.environ["MERMAID_VALIDATOR_PORT"] = "3002"
        os.environ["MERMAID_VALIDATOR_ENABLED"] = "false"

        config = ValidatorConfig()

        assert config.port == 3002
        assert config.enabled is False

    def test_base_url_property(self):
        """Test base URL generation"""
        config = ValidatorConfig(host="example.com", port=8080)

        assert config.base_url == "http://example.com:8080"

    def test_health_url_property(self):
        """Test health URL generation"""
        config = ValidatorConfig()

        assert config.health_url == "http://localhost:3001/health"

    def test_validate_url_property(self):
        """Test validate URL generation"""
        config = ValidatorConfig()

        assert config.validate_url == "http://localhost:3001/validate"

    def test_script_path_auto_detection(self):
        """Test automatic script path detection"""
        config = ValidatorConfig()

        assert config.script_path is not None
        assert config.script_path.name == "server.js"

    def test_script_path_custom(self, tmp_path):
        """Test custom script path"""
        script_file = tmp_path / "custom_server.js"
        script_file.write_text("console.log('test');")

        config = ValidatorConfig(script_path=script_file)

        assert config.script_path == script_file

    def test_script_not_found_error(self, tmp_path):
        """Test error when script not found"""
        nonexistent = tmp_path / "nonexistent.js"

        with pytest.raises(FileNotFoundError):
            ValidatorConfig(script_path=nonexistent)

    def test_get_config_singleton(self):
        """Test config singleton pattern"""
        config1 = get_config()
        config2 = get_config()

        assert config1 is config2

    def test_reset_config(self):
        """Test config reset"""
        config1 = get_config()
        reset_config()
        config2 = get_config()

        assert config1 is not config2
```

---

### Step 3: Unit Tests - Exceptions

**File**: `tests/unit/test_exceptions.py`

```python
"""
Unit tests for custom exceptions.
"""

import pytest

from services.mermaid_validator.exceptions import (
    MermaidValidatorError,
    SubprocessStartupError,
    SubprocessUnavailable,
    ValidationTimeout
)


@pytest.mark.unit
class TestExceptions:
    """Test custom exception classes"""

    def test_base_exception(self):
        """Test base exception"""
        exc = MermaidValidatorError("Test error")

        assert str(exc) == "Test error"
        assert isinstance(exc, Exception)

    def test_subprocess_startup_error(self):
        """Test subprocess startup error"""
        exc = SubprocessStartupError("Failed to start")

        assert str(exc) == "Failed to start"
        assert isinstance(exc, MermaidValidatorError)

    def test_subprocess_unavailable(self):
        """Test subprocess unavailable error"""
        exc = SubprocessUnavailable("Not reachable")

        assert str(exc) == "Not reachable"
        assert isinstance(exc, MermaidValidatorError)

    def test_validation_timeout(self):
        """Test validation timeout error"""
        exc = ValidationTimeout("Timeout", timeout=10)

        assert str(exc) == "Timeout"
        assert exc.timeout == 10
        assert isinstance(exc, MermaidValidatorError)
```

---

### Step 4: Integration Tests - Subprocess Manager

**File**: `tests/integration/test_subprocess_integration.py`

```python
"""
Integration tests for subprocess manager with real Node.js process.
"""

import pytest
import asyncio
from pathlib import Path

from services.mermaid_validator.subprocess_manager import MermaidSubprocessManager
from services.mermaid_validator.config import ValidatorConfig
from services.mermaid_validator.exceptions import SubprocessStartupError


@pytest.mark.integration
@pytest.mark.subprocess
class TestSubprocessIntegration:
    """Integration tests with real subprocess"""

    @pytest.fixture
    def test_config(self):
        """Test configuration"""
        return ValidatorConfig(
            port=3099,  # Different port for testing
            startup_timeout=15,
            health_check_interval=5
        )

    @pytest.mark.asyncio
    async def test_full_lifecycle(self, test_config):
        """Test complete subprocess lifecycle"""
        manager = MermaidSubprocessManager(test_config)

        # Start
        await manager.start()
        assert manager.is_running
        assert manager.is_healthy

        # Health check
        is_healthy = await manager.health_check()
        assert is_healthy

        # Metrics
        metrics = manager.get_metrics()
        assert metrics["running"]
        assert metrics["pid"] > 0
        assert metrics["cpu_percent"] >= 0
        assert metrics["memory_mb"] > 0

        # Stop
        await manager.stop()
        assert not manager.is_running

    @pytest.mark.asyncio
    async def test_context_manager(self, test_config):
        """Test async context manager"""
        async with MermaidSubprocessManager(test_config) as manager:
            assert manager.is_running

            is_healthy = await manager.health_check()
            assert is_healthy

        # Should be stopped after context
        assert not manager.is_running

    @pytest.mark.asyncio
    async def test_restart(self, test_config):
        """Test subprocess restart"""
        manager = MermaidSubprocessManager(test_config)

        await manager.start()
        original_pid = manager.process.pid

        await manager.restart()
        new_pid = manager.process.pid

        assert new_pid != original_pid
        assert manager.is_running

        await manager.stop()

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_health_monitoring(self, test_config):
        """Test automatic health monitoring"""
        # Very short health check interval for testing
        test_config.health_check_interval = 2
        test_config.max_consecutive_failures = 2

        manager = MermaidSubprocessManager(test_config)
        await manager.start()

        # Wait for health monitoring to run
        await asyncio.sleep(5)

        # Should still be healthy
        assert manager.is_healthy

        await manager.stop()

    @pytest.mark.asyncio
    async def test_invalid_script_path(self):
        """Test error with invalid script path"""
        config = ValidatorConfig(
            script_path=Path("/nonexistent/script.js")
        )

        with pytest.raises(FileNotFoundError):
            config = ValidatorConfig(script_path=Path("/nonexistent/script.js"))
```

---

### Step 5: Integration Tests - Validator Client

**File**: `tests/integration/test_client_integration.py`

```python
"""
Integration tests for validator client with real subprocess.
"""

import pytest

from services.mermaid_validator import MermaidSubprocessManager, MermaidValidatorClient
from services.mermaid_validator.config import ValidatorConfig


@pytest.mark.integration
@pytest.mark.subprocess
class TestClientIntegration:
    """Integration tests for validator client"""

    @pytest.fixture
    async def running_validator(self):
        """Fixture providing running validator"""
        config = ValidatorConfig(port=3098)
        manager = MermaidSubprocessManager(config)
        await manager.start()

        yield manager

        await manager.stop()

    @pytest.mark.asyncio
    async def test_validate_valid_diagram(self, running_validator):
        """Test validation of valid diagram"""
        client = MermaidValidatorClient()

        result = await client.validate("""
classDiagram
    class User {
        +String name
        +String email
        +login()
    }
""")

        assert result["valid"] is True
        assert result["diagram_type"] == "classDiagram"
        assert "code" in result

    @pytest.mark.asyncio
    async def test_validate_invalid_diagram(self, running_validator):
        """Test validation of invalid diagram"""
        client = MermaidValidatorClient()

        result = await client.validate("""
classDiagra
    class User {
        invalid syntax here
    }
""")

        assert result["valid"] is False
        assert "errors" in result
        assert len(result["errors"]) > 0

    @pytest.mark.asyncio
    async def test_multiple_validations(self, running_validator):
        """Test multiple concurrent validations"""
        client = MermaidValidatorClient()

        diagrams = [
            "classDiagram\n  class A",
            "classDiagram\n  class B",
            "classDiagram\n  class C",
        ]

        # Validate concurrently
        results = await asyncio.gather(*[
            client.validate(diagram)
            for diagram in diagrams
        ])

        assert len(results) == 3
        assert all(r["valid"] for r in results)

    @pytest.mark.asyncio
    async def test_health_check(self, running_validator):
        """Test client health check"""
        client = MermaidValidatorClient()

        is_healthy = await client.health_check()

        assert is_healthy is True


# Add missing import
import asyncio
```

---

### Step 6: Integration Tests - Workflow

**File**: `tests/integration/test_workflow_validation.py`

```python
"""
Integration tests for workflow with validation.
"""

import pytest
from unittest.mock import AsyncMock, patch

from workflows.class_diagram_workflow.workflow import class_diagram_graph


@pytest.mark.integration
class TestWorkflowValidation:
    """Integration tests for validated workflows"""

    @pytest.fixture
    def mock_validator(self):
        """Mock validator for controlled testing"""
        validator = AsyncMock()
        validator.validate.return_value = {
            "valid": True,
            "code": "classDiagram\n  class User",
            "diagram_type": "classDiagram",
            "timestamp": 1699999999,
            "duration_ms": 150
        }
        return validator

    @pytest.mark.asyncio
    async def test_workflow_with_valid_diagram(self, mock_validator):
        """Test complete workflow with valid diagram"""
        initial_state = {
            "user_input": "Create a User class with name and email",
            "retry_count": 0,
            "validated": False,
            "app_context": {"validator": mock_validator}
        }

        result = await class_diagram_graph.ainvoke(initial_state)

        # Should complete successfully
        assert result["validated"] is True
        assert result["retry_count"] == 0
        assert "metadata" in result
        assert result["metadata"]["validation_status"] == "valid"

    @pytest.mark.asyncio
    async def test_workflow_with_retry(self, mock_validator):
        """Test workflow with one retry"""
        # First call: invalid, second call: valid
        mock_validator.validate.side_effect = [
            {
                "valid": False,
                "errors": [{"message": "Syntax error", "line": 1}]
            },
            {
                "valid": True,
                "code": "classDiagram\n  class User",
                "diagram_type": "classDiagram"
            }
        ]

        initial_state = {
            "user_input": "Create a User class",
            "retry_count": 0,
            "validated": False,
            "app_context": {"validator": mock_validator}
        }

        result = await class_diagram_graph.ainvoke(initial_state)

        assert result["validated"] is True
        assert result["retry_count"] == 1
        assert mock_validator.validate.call_count == 2

    @pytest.mark.asyncio
    async def test_workflow_max_retries(self, mock_validator):
        """Test workflow with max retries"""
        # Always return invalid
        mock_validator.validate.return_value = {
            "valid": False,
            "errors": [{"message": "Persistent error"}]
        }

        initial_state = {
            "user_input": "Create invalid diagram",
            "retry_count": 0,
            "validated": False,
            "app_context": {"validator": mock_validator}
        }

        result = await class_diagram_graph.ainvoke(initial_state)

        assert result["validated"] is False
        assert result["retry_count"] == 3
        assert mock_validator.validate.call_count == 4  # Initial + 3 retries
        assert result["metadata"]["validation_status"] == "invalid"

    @pytest.mark.asyncio
    async def test_workflow_without_validator(self):
        """Test workflow graceful degradation without validator"""
        initial_state = {
            "user_input": "Create a User class",
            "retry_count": 0,
            "validated": False,
            "app_context": {"validator": None}  # No validator
        }

        result = await class_diagram_graph.ainvoke(initial_state)

        # Should complete but marked as unvalidated
        assert result["validated"] is False
        assert "warning" in result.get("validation_result", {})
```

---

### Step 7: End-to-End Tests

**File**: `tests/e2e/test_full_stack.py`

```python
"""
End-to-end tests with real subprocess and workflow.
"""

import pytest
from httpx import AsyncClient

from main import app
from services.mermaid_validator import MermaidSubprocessManager


@pytest.mark.e2e
@pytest.mark.subprocess
@pytest.mark.slow
class TestFullStack:
    """End-to-end tests with full stack"""

    @pytest.fixture
    async def test_app(self):
        """Fixture providing test application"""
        # Start validator
        from services.mermaid_validator.config import ValidatorConfig
        config = ValidatorConfig(port=3097)
        validator = MermaidSubprocessManager(config)
        await validator.start()

        # Inject into app
        app.state.validator = validator

        yield app

        # Cleanup
        await validator.stop()

    @pytest.mark.asyncio
    async def test_generate_valid_class_diagram(self, test_app):
        """Test full diagram generation with validation"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            response = await client.post(
                "/generate/class-diagram",
                json={
                    "description": "Create a simple User class with name attribute"
                }
            )

            assert response.status_code == 200
            data = response.json()

            assert data["type"] == "class_diagram"
            assert "classDiagram" in data["detail"]
            assert data["metadata"]["validated"] is True
            assert data["metadata"]["retry_count"] >= 0

    @pytest.mark.asyncio
    async def test_health_check(self, test_app):
        """Test health check endpoint"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            response = await client.get("/health")

            assert response.status_code == 200
            data = response.json()

            assert data["status"] in ["healthy", "degraded"]
            assert data["api"] == "ok"
            assert "validator" in data
```

---

### Step 8: Performance Tests

**File**: `tests/performance/test_validation_performance.py`

```python
"""
Performance tests for validation system.
"""

import pytest
import time
import asyncio
from statistics import mean, stdev

from services.mermaid_validator import MermaidSubprocessManager, MermaidValidatorClient
from services.mermaid_validator.config import ValidatorConfig


@pytest.mark.slow
@pytest.mark.subprocess
class TestValidationPerformance:
    """Performance tests"""

    @pytest.fixture
    async def running_validator(self):
        """Fixture providing running validator"""
        config = ValidatorConfig(port=3096)
        manager = MermaidSubprocessManager(config)
        await manager.start()

        yield manager

        await manager.stop()

    @pytest.mark.asyncio
    async def test_validation_latency(self, running_validator):
        """Test single validation latency"""
        client = MermaidValidatorClient()

        diagram = "classDiagram\n  class User"

        # Warmup
        await client.validate(diagram)

        # Measure
        latencies = []
        for _ in range(10):
            start = time.perf_counter()
            await client.validate(diagram)
            latency = (time.perf_counter() - start) * 1000  # ms
            latencies.append(latency)

        avg_latency = mean(latencies)
        std_latency = stdev(latencies)

        print(f"\nAverage latency: {avg_latency:.2f}ms (±{std_latency:.2f}ms)")

        # Should be under 500ms
        assert avg_latency < 500

    @pytest.mark.asyncio
    async def test_concurrent_validations(self, running_validator):
        """Test concurrent validation performance"""
        client = MermaidValidatorClient()

        diagram = "classDiagram\n  class User"

        # Measure concurrent requests
        start = time.perf_counter()

        results = await asyncio.gather(*[
            client.validate(diagram)
            for _ in range(20)
        ])

        duration = time.perf_counter() - start

        print(f"\n20 concurrent validations: {duration:.2f}s")
        print(f"Throughput: {len(results) / duration:.2f} req/s")

        assert all(r["valid"] for r in results)
        assert duration < 10  # Should complete in < 10s

    @pytest.mark.asyncio
    async def test_subprocess_startup_time(self):
        """Test subprocess startup performance"""
        config = ValidatorConfig(port=3095)
        manager = MermaidSubprocessManager(config)

        start = time.perf_counter()
        await manager.start()
        startup_time = time.perf_counter() - start

        print(f"\nSubprocess startup: {startup_time:.2f}s")

        assert startup_time < 5  # Should start in < 5s

        await manager.stop()
```

---

### Step 9: Test Utilities

**File**: `tests/conftest.py`

```python
"""
Pytest configuration and shared fixtures.
"""

import pytest
import asyncio
import os
from pathlib import Path


# Configure asyncio for pytest
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Set test environment variables
@pytest.fixture(scope="session", autouse=True)
def test_env():
    """Set test environment variables"""
    os.environ["MERMAID_VALIDATOR_ENABLED"] = "true"
    os.environ["MERMAID_VALIDATOR_LOG_LEVEL"] = "DEBUG"
    os.environ["OPENROUTER_API_KEY"] = os.getenv("OPENROUTER_API_KEY", "test-key")


# Cleanup temp files
@pytest.fixture(autouse=True)
def cleanup_temp_files(tmp_path):
    """Clean up temporary files after each test"""
    yield
    # Cleanup logic if needed


# Mock fixtures
@pytest.fixture
def mock_valid_diagram():
    """Mock valid diagram response"""
    return {
        "valid": True,
        "code": "classDiagram\n  class User",
        "diagram_type": "classDiagram",
        "timestamp": 1699999999,
        "duration_ms": 150
    }


@pytest.fixture
def mock_invalid_diagram():
    """Mock invalid diagram response"""
    return {
        "valid": False,
        "code": "invalid code",
        "errors": [
            {
                "message": "Syntax error",
                "type": "SyntaxError",
                "line": 1,
                "column": 5
            }
        ],
        "timestamp": 1699999999
    }
```

---

## ✅ Running Tests

### Run All Tests

```powershell
# Run all tests with coverage
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_config.py -v
```

### Run by Marker

```powershell
# Run only unit tests (fast)
pytest -m unit

# Run integration tests
pytest -m integration

# Run e2e tests
pytest -m e2e

# Skip slow tests
pytest -m "not slow"

# Run subprocess tests
pytest -m subprocess
```

### Coverage Report

```powershell
# Generate HTML coverage report
pytest --cov=services.mermaid_validator --cov=workflows --cov-report=html

# Open in browser
Start-Process .\htmlcov\index.html
```

---

## ✅ Verification Checklist

- [ ] pytest.ini configured
- [ ] Unit tests for config (10+ tests)
- [ ] Unit tests for exceptions
- [ ] Integration tests for subprocess (5+ tests)
- [ ] Integration tests for client (5+ tests)
- [ ] Integration tests for workflow (5+ tests)
- [ ] End-to-end tests (2+ tests)
- [ ] Performance tests (3+ tests)
- [ ] Test utilities in conftest.py
- [ ] Coverage > 90%
- [ ] All tests passing

---

## 🎯 Commit Time!

```powershell
cd d:\Do_an_tot_nghiep\ba_copilot_ai

git add pytest.ini
git add tests/

git commit -m "test: add comprehensive tests for validation system

- Configure pytest with coverage and async support
- Implement unit tests for config and exceptions
- Add integration tests for subprocess manager
- Create integration tests for validator client
- Implement workflow validation tests
- Add end-to-end tests with full stack
- Create performance benchmarks
- Configure test markers and fixtures

Test Coverage:
  - Unit tests: Config, exceptions, utilities
  - Integration: Subprocess, client, workflow
  - E2E: Full API with real subprocess
  - Performance: Latency, throughput, startup

Pytest Configuration:
  - Async support with asyncio_mode=auto
  - Coverage target: 90%
  - HTML and XML coverage reports
  - Test markers for selective execution
  - 30s timeout for hanging tests

Test Markers:
  - unit: Fast unit tests
  - integration: Multi-component tests
  - e2e: Full stack tests
  - slow: Tests > 1 second
  - subprocess: Requires real Node.js process

Performance Targets:
  - Validation latency: < 500ms
  - Subprocess startup: < 5s
  - Concurrent throughput: > 2 req/s

Refs: #OPS-317"
```

---

## 🐛 Troubleshooting

### Issue: Tests timeout

**Symptom**:

```
FAILED tests/test_subprocess.py::test_start - TIMEOUT
```

**Solution**:

```python
# Increase timeout for slow tests
@pytest.mark.timeout(60)
async def test_slow_operation():
    ...
```

### Issue: Port conflicts in tests

**Symptom**:

```
OSError: [Errno 48] Address already in use
```

**Solution**:

```python
# Use different ports for each test
@pytest.fixture
def unique_port():
    return random.randint(30000, 40000)
```

---

## 📚 Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [Testing Best Practices](https://testdriven.io/blog/testing-best-practices/)

---

**Next Phase**: [07_DEPLOYMENT_VERIFICATION.md](./07_DEPLOYMENT_VERIFICATION.md) →

---

**Phase 6 Complete** ✅  
**Est. Completion Time**: 90-120 minutes  
**Commit**: `test: add comprehensive tests for validation system`
