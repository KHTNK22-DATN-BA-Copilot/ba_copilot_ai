# Phase 5: Integration Testing

## 🎯 Objective

Create comprehensive tests for the Mermaid validation integration, ensuring all components work together correctly and edge cases are handled.

**Estimated Time**: 30-35 minutes  
**Commit Message**: `test: add comprehensive tests for diagram validation integration`

---

## 🏗️ Testing Strategy

### Test Pyramid

```
           ┌─────────────────┐
           │  E2E Tests (5)  │  ← Full API → LangGraph → MCP
           ├─────────────────┤
           │ Integration (8) │  ← LangGraph + MCP mock
           ├─────────────────┤
           │ Unit Tests (12) │  ← Individual functions
           └─────────────────┘
```

**Test Distribution**:

- **Unit Tests (60%)**: Individual nodes, functions, utilities
- **Integration Tests (30%)**: Workflow, multi-component interactions
- **E2E Tests (10%)**: Full API requests through validation

---

## 🔍 Deep Dive: Testing Approaches

### Unit vs. Integration vs. E2E

| Aspect              | Unit            | Integration         | E2E            |
| ------------------- | --------------- | ------------------- | -------------- |
| **Scope**           | Single function | Multiple components | Full system    |
| **External Deps**   | All mocked      | Some mocked         | Real services  |
| **Speed**           | <100ms          | <1s                 | >2s            |
| **Flakiness**       | Very low        | Low                 | Medium         |
| **Debugging**       | Easy            | Moderate            | Hard           |
| **CI/CD Frequency** | Every commit    | Every PR            | Nightly/deploy |

**Our Strategy**:

- **Unit**: Test each node independently with mocked dependencies
- **Integration**: Test LangGraph workflow with mocked MCP
- **E2E**: Test full FastAPI → LangGraph → MCP with real MCP server

---

## 🛠️ Implementation Steps

### Step 1: Setup Test Infrastructure

**File**: `tests/__init__.py`

```python
"""
Test package for BA Copilot AI service.
"""
```

**File**: `tests/conftest.py`

````python
"""
Pytest configuration and shared fixtures.

This module provides:
- Mock MCP client fixtures
- Test data fixtures
- FastAPI test client
- Async test utilities
"""

import pytest
import asyncio
from typing import AsyncGenerator, Dict, Any
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch

# Import application
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from services.mcp_client import MCPClient


# ============================================
# Pytest Configuration
# ============================================

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, no external dependencies)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (require mocked services)"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests (require real services)"
    )
    config.addinivalue_line(
        "markers", "slow: Slow tests (>1s execution time)"
    )


# ============================================
# Async Test Utilities
# ============================================

@pytest.fixture(scope="session")
def event_loop():
    """
    Create an instance of the default event loop for the test session.

    Required for pytest-asyncio to work properly with session-scoped fixtures.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================
# FastAPI Test Client
# ============================================

@pytest.fixture
def client() -> TestClient:
    """
    Create FastAPI test client.

    Usage:
        def test_health(client):
            response = client.get("/health")
            assert response.status_code == 200
    """
    return TestClient(app)


# ============================================
# Mock MCP Client
# ============================================

@pytest.fixture
def mock_mcp_client_success():
    """
    Mock MCP client that always returns valid diagrams.

    Usage:
        @pytest.mark.asyncio
        async def test_validation(mock_mcp_client_success):
            with patch("services.mcp_client.MCPClient", return_value=mock_mcp_client_success):
                result = await validate_mermaid("graph TD\nA-->B")
                assert result["valid"] is True
    """
    mock_client = AsyncMock(spec=MCPClient)

    # Mock __aenter__ for context manager
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    # Mock validate_mermaid method
    mock_client.validate_mermaid = AsyncMock(return_value={
        "valid": True,
        "code": "graph TD\nA-->B",
        "errors": []
    })

    # Mock health_check method
    mock_client.health_check = AsyncMock(return_value=True)

    return mock_client


@pytest.fixture
def mock_mcp_client_invalid():
    """
    Mock MCP client that returns validation errors.

    Usage:
        @pytest.mark.asyncio
        async def test_invalid_diagram(mock_mcp_client_invalid):
            with patch("services.mcp_client.MCPClient", return_value=mock_mcp_client_invalid):
                result = await validate_mermaid("invalid code")
                assert result["valid"] is False
    """
    mock_client = AsyncMock(spec=MCPClient)

    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    mock_client.validate_mermaid = AsyncMock(return_value={
        "valid": False,
        "code": "invalid code",
        "errors": ["Syntax error at line 1: Invalid diagram type"]
    })

    mock_client.health_check = AsyncMock(return_value=True)

    return mock_client


@pytest.fixture
def mock_mcp_client_unavailable():
    """
    Mock MCP client that simulates server unavailability.

    Usage:
        @pytest.mark.asyncio
        async def test_mcp_unavailable(mock_mcp_client_unavailable):
            with patch("services.mcp_client.MCPClient", return_value=mock_mcp_client_unavailable):
                # Should handle gracefully
                result = await validate_with_fallback("graph TD\nA-->B")
    """
    from services.mcp_client import MCPServerUnavailable

    mock_client = AsyncMock(spec=MCPClient)

    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    # Raise exception on validation
    mock_client.validate_mermaid = AsyncMock(
        side_effect=MCPServerUnavailable("MCP server unavailable")
    )

    mock_client.health_check = AsyncMock(return_value=False)

    return mock_client


# ============================================
# Test Data Fixtures
# ============================================

@pytest.fixture
def valid_mermaid_code() -> str:
    """Valid Mermaid class diagram code"""
    return """```mermaid
classDiagram
    class User {
        +String name
        +String email
        +login()
    }
    class Product {
        +String title
        +float price
    }
    User --> Product : purchases
```"""


@pytest.fixture
def invalid_mermaid_code() -> str:
    """Invalid Mermaid class diagram code"""
    return """```mermaid
classDiagram
    class User {
        +String name
        INVALID SYNTAX HERE
    }
```"""


@pytest.fixture
def complex_user_request() -> str:
    """Complex user request for class diagram"""
    return "Create a class diagram for an e-commerce system with User, Product, Order, and Payment classes. Include appropriate relationships and attributes."


@pytest.fixture
def simple_user_request() -> str:
    """Simple user request for class diagram"""
    return "Create a User class with name and email attributes"


# ============================================
# Mock OpenAI/LLM Responses
# ============================================

@pytest.fixture
def mock_openai_valid_response(valid_mermaid_code):
    """
    Mock OpenAI response with valid Mermaid code.

    Usage:
        def test_generation(mock_openai_valid_response):
            with patch("openai.OpenAI") as mock_openai:
                mock_openai.return_value.chat.completions.create.return_value = mock_openai_valid_response
                result = generate_diagram("Create User class")
    """
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = valid_mermaid_code
    return mock_response


@pytest.fixture
def mock_openai_invalid_response(invalid_mermaid_code):
    """Mock OpenAI response with invalid Mermaid code"""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = invalid_mermaid_code
    return mock_response
````

**Key Testing Utilities Explained**:

1. **Pytest Markers**

   ```python
   @pytest.mark.unit
   @pytest.mark.integration
   @pytest.mark.e2e
   @pytest.mark.slow
   ```

   - **Usage**: Filter tests by type
   - **Example**: `pytest -m unit` (run only unit tests)

2. **Async Fixtures**

   ```python
   @pytest.fixture(scope="session")
   def event_loop():
       ...
   ```

   - **Why**: pytest-asyncio needs event loop for async tests
   - **Scope**: Session-wide to avoid recreating

3. **Mock Context Managers**
   ```python
   mock_client.__aenter__.return_value = mock_client
   mock_client.__aexit__.return_value = None
   ```
   - **Why**: MCPClient uses `async with` syntax
   - **Without it**: Tests fail with "object not iterable"

---

### Step 2: Create Unit Tests for MCP Client

**File**: `tests/test_mcp_client.py`

```python
"""
Unit tests for MCP Client service.

Tests cover:
- Successful validation
- Invalid diagram handling
- Server unavailability
- Error handling
- Health checks
"""

import pytest
from unittest.mock import patch, AsyncMock
import httpx

from services.mcp_client import (
    MCPClient,
    MCPServerUnavailable,
    MCPValidationError,
    validate_mermaid_code
)


@pytest.mark.unit
@pytest.mark.asyncio
class TestMCPClient:
    """Unit tests for MCPClient class"""

    async def test_validate_valid_diagram(self, mocker):
        """Test validation of syntactically correct Mermaid code"""
        # Mock httpx response
        mock_response = mocker.Mock()
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "result": {
                "content": [
                    {"type": "text", "text": "Valid Mermaid diagram"}
                ]
            },
            "id": 1
        }
        mock_response.raise_for_status = mocker.Mock()

        mock_post = mocker.patch("httpx.AsyncClient.post", return_value=mock_response)

        # Test validation
        async with MCPClient() as client:
            result = await client.validate_mermaid("graph TD\nA-->B")

        assert result["valid"] is True
        assert result["code"] == "graph TD\nA-->B"
        assert result["errors"] == []
        mock_post.assert_called_once()

    async def test_validate_invalid_diagram(self, mocker):
        """Test validation of invalid Mermaid code"""
        # Mock error response
        mock_response = mocker.Mock()
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "error": {
                "code": -32602,
                "message": "Invalid Mermaid syntax",
                "data": {
                    "errors": ["Line 2: Invalid arrow syntax"]
                }
            },
            "id": 1
        }
        mock_response.raise_for_status = mocker.Mock()

        mocker.patch("httpx.AsyncClient.post", return_value=mock_response)

        # Test validation
        async with MCPClient() as client:
            result = await client.validate_mermaid("graph TD\nA--INVALID-->B")

        assert result["valid"] is False
        assert "Line 2: Invalid arrow syntax" in result["errors"]

    async def test_server_timeout(self, mocker):
        """Test handling of MCP server timeout"""
        # Mock timeout exception
        mocker.patch(
            "httpx.AsyncClient.post",
            side_effect=httpx.TimeoutException("Request timed out")
        )

        # Should raise MCPServerUnavailable
        with pytest.raises(MCPServerUnavailable) as exc_info:
            async with MCPClient(timeout=5) as client:
                await client.validate_mermaid("graph TD\nA-->B")

        assert "timeout" in str(exc_info.value).lower()

    async def test_server_connection_error(self, mocker):
        """Test handling of MCP server connection failure"""
        # Mock connection error
        mocker.patch(
            "httpx.AsyncClient.post",
            side_effect=httpx.ConnectError("Cannot connect to server")
        )

        # Should raise MCPServerUnavailable
        with pytest.raises(MCPServerUnavailable) as exc_info:
            async with MCPClient() as client:
                await client.validate_mermaid("graph TD\nA-->B")

        assert "connect" in str(exc_info.value).lower()

    async def test_health_check_healthy(self, mocker):
        """Test health check when MCP server is healthy"""
        # Mock successful validation
        mock_response = mocker.Mock()
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "result": {
                "content": [{"type": "text", "text": "Valid Mermaid diagram"}]
            },
            "id": 1
        }
        mock_response.raise_for_status = mocker.Mock()

        mocker.patch("httpx.AsyncClient.post", return_value=mock_response)

        # Test health check
        async with MCPClient() as client:
            is_healthy = await client.health_check()

        assert is_healthy is True

    async def test_health_check_unhealthy(self, mocker):
        """Test health check when MCP server is unavailable"""
        # Mock connection error
        mocker.patch(
            "httpx.AsyncClient.post",
            side_effect=httpx.ConnectError("Cannot connect")
        )

        # Test health check
        async with MCPClient() as client:
            is_healthy = await client.health_check()

        assert is_healthy is False

    async def test_validate_empty_code(self):
        """Test validation with empty diagram code"""
        async with MCPClient() as client:
            result = await client.validate_mermaid("")

        # Should handle gracefully (server may return error)
        assert "valid" in result
        assert "errors" in result

    async def test_custom_base_url(self, mocker):
        """Test MCP client with custom base URL"""
        mock_response = mocker.Mock()
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "result": {"content": [{"type": "text", "text": "Valid"}]},
            "id": 1
        }
        mock_response.raise_for_status = mocker.Mock()

        mock_post = mocker.patch("httpx.AsyncClient.post", return_value=mock_response)

        # Test with custom URL
        custom_url = "http://custom-mcp-server:4000"
        async with MCPClient(base_url=custom_url) as client:
            await client.validate_mermaid("graph TD\nA-->B")

        # Verify custom URL was used
        call_args = mock_post.call_args
        assert call_args[0][0] == custom_url


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_mermaid_code_convenience_function(mocker):
    """Test standalone validate_mermaid_code function"""
    # Mock successful validation
    mock_response = mocker.Mock()
    mock_response.json.return_value = {
        "jsonrpc": "2.0",
        "result": {
            "content": [{"type": "text", "text": "Valid"}]
        },
        "id": 1
    }
    mock_response.raise_for_status = mocker.Mock()

    mocker.patch("httpx.AsyncClient.post", return_value=mock_response)

    # Test convenience function
    result = await validate_mermaid_code("graph TD\nA-->B")

    assert result["valid"] is True
```

**Run unit tests**:

```powershell
pytest tests/test_mcp_client.py -v -m unit
```

**Expected Output**:

```
tests/test_mcp_client.py::TestMCPClient::test_validate_valid_diagram PASSED
tests/test_mcp_client.py::TestMCPClient::test_validate_invalid_diagram PASSED
tests/test_mcp_client.py::TestMCPClient::test_server_timeout PASSED
tests/test_mcp_client.py::TestMCPClient::test_server_connection_error PASSED
tests/test_mcp_client.py::TestMCPClient::test_health_check_healthy PASSED
tests/test_mcp_client.py::TestMCPClient::test_health_check_unhealthy PASSED
tests/test_mcp_client.py::TestMCPClient::test_validate_empty_code PASSED
tests/test_mcp_client.py::TestMCPClient::test_custom_base_url PASSED
tests/test_mcp_client.py::test_validate_mermaid_code_convenience_function PASSED

=========== 9 passed in 0.45s ===========
```

---

### Step 3: Create Integration Tests for Workflow

**File**: `tests/test_class_diagram_workflow.py`

```python
"""
Integration tests for class diagram workflow with validation.

Tests cover:
- Full workflow execution
- Validation node integration
- Retry logic
- Error handling
- State management
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from workflows.class_diagram_workflow import (
    class_diagram_graph,
    generate_class_diagram_description,
    validate_diagram_node,
    fix_diagram_node,
    format_response_node,
    should_retry_fix
)


@pytest.mark.integration
class TestClassDiagramWorkflow:
    """Integration tests for class diagram workflow"""

    def test_workflow_with_valid_diagram(
        self,
        simple_user_request,
        valid_mermaid_code,
        mock_openai_valid_response,
        mock_mcp_client_success
    ):
        """Test complete workflow with valid diagram generation"""
        # Mock OpenAI and MCP
        with patch("openai.OpenAI") as mock_openai, \
             patch("services.mcp_client.MCPClient", return_value=mock_mcp_client_success):

            mock_openai.return_value.chat.completions.create.return_value = mock_openai_valid_response

            # Execute workflow
            result = class_diagram_graph.invoke({
                "user_message": simple_user_request
            })

        # Verify response
        assert "response" in result
        response = result["response"]
        assert response["type"] == "class_diagram"
        assert "detail" in response
        assert response.get("metadata", {}).get("validated") is True
        assert response.get("metadata", {}).get("retry_count") == 0

    def test_workflow_with_invalid_diagram_and_fix(
        self,
        simple_user_request,
        invalid_mermaid_code,
        valid_mermaid_code,
        mock_mcp_client_invalid,
        mock_mcp_client_success
    ):
        """Test workflow with invalid diagram that gets fixed"""
        # First call: invalid diagram
        # Second call: valid diagram (after fix)
        mock_openai_responses = [
            MagicMock(choices=[MagicMock(message=MagicMock(content=invalid_mermaid_code))]),
            MagicMock(choices=[MagicMock(message=MagicMock(content=valid_mermaid_code))])
        ]

        # MCP responses: first invalid, then valid
        mock_mcp_invalid = AsyncMock()
        mock_mcp_invalid.__aenter__.return_value = mock_mcp_invalid
        mock_mcp_invalid.__aexit__.return_value = None
        mock_mcp_invalid.validate_mermaid = AsyncMock(side_effect=[
            {"valid": False, "code": invalid_mermaid_code, "errors": ["Syntax error"]},
            {"valid": True, "code": valid_mermaid_code, "errors": []}
        ])

        with patch("openai.OpenAI") as mock_openai, \
             patch("services.mcp_client.MCPClient", return_value=mock_mcp_invalid):

            mock_openai.return_value.chat.completions.create.side_effect = mock_openai_responses

            # Execute workflow
            result = class_diagram_graph.invoke({
                "user_message": simple_user_request
            })

        # Verify retry occurred
        response = result["response"]
        assert response.get("metadata", {}).get("validated") is True
        assert response.get("metadata", {}).get("retry_count") == 1

    def test_workflow_max_retries_exceeded(
        self,
        simple_user_request,
        invalid_mermaid_code
    ):
        """Test workflow when max retries are exceeded"""
        # Mock OpenAI to always return invalid code
        mock_response = MagicMock(
            choices=[MagicMock(message=MagicMock(content=invalid_mermaid_code))]
        )

        # Mock MCP to always return invalid
        mock_mcp = AsyncMock()
        mock_mcp.__aenter__.return_value = mock_mcp
        mock_mcp.__aexit__.return_value = None
        mock_mcp.validate_mermaid = AsyncMock(return_value={
            "valid": False,
            "code": invalid_mermaid_code,
            "errors": ["Persistent syntax error"]
        })

        with patch("openai.OpenAI") as mock_openai, \
             patch("services.mcp_client.MCPClient", return_value=mock_mcp):

            mock_openai.return_value.chat.completions.create.return_value = mock_response

            # Execute workflow
            result = class_diagram_graph.invoke({
                "user_message": simple_user_request
            })

        # Verify max retries reached
        response = result["response"]
        assert response.get("metadata", {}).get("retry_count") == 3
        assert response.get("metadata", {}).get("validated") is False
        assert "errors" in response.get("metadata", {})

    def test_workflow_with_mcp_unavailable(
        self,
        simple_user_request,
        valid_mermaid_code,
        mock_openai_valid_response,
        mock_mcp_client_unavailable
    ):
        """Test workflow with MCP server unavailable (graceful degradation)"""
        with patch("openai.OpenAI") as mock_openai, \
             patch("services.mcp_client.MCPClient", return_value=mock_mcp_client_unavailable):

            mock_openai.return_value.chat.completions.create.return_value = mock_openai_valid_response

            # Execute workflow
            result = class_diagram_graph.invoke({
                "user_message": simple_user_request
            })

        # Should complete successfully with warning
        response = result["response"]
        assert "detail" in response
        assert response.get("metadata", {}).get("warning") is not None


@pytest.mark.integration
@pytest.mark.asyncio
class TestValidationNode:
    """Test validation node in isolation"""

    async def test_validate_node_success(self, valid_mermaid_code, mock_mcp_client_success):
        """Test validation node with valid diagram"""
        state = {
            "user_message": "Test",
            "raw_diagram": valid_mermaid_code,
            "validated_diagram": valid_mermaid_code,
            "retry_count": 0,
            "errors": []
        }

        with patch("services.mcp_client.MCPClient", return_value=mock_mcp_client_success):
            result = await validate_diagram_node(state)

        assert result["validation_result"]["valid"] is True
        assert result["errors"] == []

    async def test_validate_node_invalid(self, invalid_mermaid_code, mock_mcp_client_invalid):
        """Test validation node with invalid diagram"""
        state = {
            "user_message": "Test",
            "raw_diagram": invalid_mermaid_code,
            "validated_diagram": invalid_mermaid_code,
            "retry_count": 0,
            "errors": []
        }

        with patch("services.mcp_client.MCPClient", return_value=mock_mcp_client_invalid):
            result = await validate_diagram_node(state)

        assert result["validation_result"]["valid"] is False
        assert len(result["errors"]) > 0


@pytest.mark.integration
class TestConditionalEdge:
    """Test conditional routing logic"""

    def test_should_retry_valid_diagram(self):
        """Test routing when diagram is valid"""
        state = {
            "validation_result": {"valid": True},
            "retry_count": 0
        }

        next_node = should_retry_fix(state)
        assert next_node == "format_response"

    def test_should_retry_invalid_first_attempt(self):
        """Test routing when diagram is invalid (first attempt)"""
        state = {
            "validation_result": {"valid": False},
            "retry_count": 0
        }

        next_node = should_retry_fix(state)
        assert next_node == "fix_diagram"

    def test_should_retry_max_attempts_reached(self):
        """Test routing when max retries reached"""
        state = {
            "validation_result": {"valid": False},
            "retry_count": 3
        }

        next_node = should_retry_fix(state)
        assert next_node == "format_response"
```

**Run integration tests**:

```powershell
pytest tests/test_class_diagram_workflow.py -v -m integration
```

---

### Step 4: Create End-to-End API Tests

**File**: `tests/test_api_e2e.py`

````python
"""
End-to-end API tests for class diagram generation with validation.

These tests require:
- FastAPI application running
- MCP server available (or mocked)
- OpenRouter API key configured
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.e2e
class TestClassDiagramAPI:
    """E2E tests for class diagram generation API"""

    def test_generate_simple_class_diagram(self, client):
        """Test generating simple class diagram via API"""
        response = client.post(
            "/api/v1/generate/class-diagram",
            json={
                "message": "Create a User class with name and email attributes"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["type"] == "diagram"
        assert data["response"]["type"] == "class_diagram"
        assert "```mermaid" in data["response"]["detail"]
        assert "classDiagram" in data["response"]["detail"]

    def test_generate_complex_class_diagram(self, client):
        """Test generating complex class diagram"""
        response = client.post(
            "/api/v1/generate/class-diagram",
            json={
                "message": "Create class diagram for e-commerce with User, Product, Order, Payment"
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Check structure
        assert "response" in data
        assert "detail" in data["response"]
        assert "metadata" in data["response"]

        # Check metadata
        metadata = data["response"]["metadata"]
        assert "validated" in metadata
        assert "retry_count" in metadata

    @pytest.mark.slow
    def test_api_validation_metadata_included(self, client):
        """Test that validation metadata is included in response"""
        response = client.post(
            "/api/v1/generate/class-diagram",
            json={
                "message": "Create a simple Book class"
            }
        )

        assert response.status_code == 200
        data = response.json()

        metadata = data["response"].get("metadata", {})
        assert "validated" in metadata
        assert isinstance(metadata["validated"], bool)
        assert "retry_count" in metadata
        assert isinstance(metadata["retry_count"], int)

    def test_api_error_handling(self, client):
        """Test API error handling with invalid request"""
        response = client.post(
            "/api/v1/generate/class-diagram",
            json={}  # Missing 'message' field
        )

        assert response.status_code == 422  # Validation error


@pytest.mark.e2e
class TestHealthEndpoint:
    """E2E tests for health check endpoint"""

    def test_health_check_includes_mcp_status(self, client):
        """Test health check includes MCP server status"""
        response = client.get("/health")

        assert response.status_code in [200, 503]  # 503 if MCP unavailable
        data = response.json()

        assert "status" in data
        assert "checks" in data
        assert "mcp_server" in data["checks"]
````

**Run E2E tests** (requires services running):

```powershell
# Start services
docker-compose up -d

# Run E2E tests
pytest tests/test_api_e2e.py -v -m e2e

# Stop services
docker-compose down
```

---

### Step 5: Add pytest Configuration

**File**: `pytest.ini`

```ini
[pytest]
# Test discovery patterns
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*

# Async support
asyncio_mode = auto

# Markers
markers =
    unit: Unit tests (fast, no external dependencies)
    integration: Integration tests (require mocked services)
    e2e: End-to-end tests (require real services)
    slow: Slow tests (>1s execution time)

# Output options
addopts =
    -v
    --strict-markers
    --tb=short
    --disable-warnings

# Coverage options
[coverage:run]
source = .
omit =
    tests/*
    */__pycache__/*
    */venv/*
    */.venv/*

[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
```

---

### Step 6: Create Test Runner Script

**File**: `scripts/run-tests.ps1`

```powershell
# Test runner script with coverage
param(
    [string]$TestType = "all",  # all, unit, integration, e2e
    [switch]$Coverage,
    [switch]$Verbose
)

Write-Host "BA Copilot AI - Test Runner" -ForegroundColor Green
Write-Host "Test Type: $TestType" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Build test command
$testCmd = "pytest"

# Add test type filter
switch ($TestType) {
    "unit" { $testCmd += " -m unit" }
    "integration" { $testCmd += " -m integration" }
    "e2e" {
        Write-Host "Starting services for E2E tests..." -ForegroundColor Yellow
        docker-compose up -d
        Start-Sleep -Seconds 10
        $testCmd += " -m e2e"
    }
    "all" { }
}

# Add coverage
if ($Coverage) {
    $testCmd += " --cov=. --cov-report=html --cov-report=term"
}

# Add verbosity
if ($Verbose) {
    $testCmd += " -vv"
}

# Run tests
Write-Host "Running: $testCmd" -ForegroundColor Yellow
Invoke-Expression $testCmd

# Cleanup for E2E
if ($TestType -eq "e2e") {
    Write-Host "`nStopping services..." -ForegroundColor Yellow
    docker-compose down
}

# Show coverage report
if ($Coverage) {
    Write-Host "`nCoverage report generated: htmlcov/index.html" -ForegroundColor Green
}
```

**Usage**:

```powershell
# Run all tests
.\scripts\run-tests.ps1

# Run only unit tests
.\scripts\run-tests.ps1 -TestType unit

# Run with coverage
.\scripts\run-tests.ps1 -Coverage

# Verbose output
.\scripts\run-tests.ps1 -Verbose
```

---

### Step 7: Run All Tests and Generate Coverage

```powershell
# Run all tests with coverage
.\scripts\run-tests.ps1 -TestType all -Coverage

# Expected output:
# ============ test session starts ============
# collected 25 items
#
# tests/test_mcp_client.py ........... [44%]
# tests/test_class_diagram_workflow.py .......... [84%]
# tests/test_api_e2e.py .... [100%]
#
# ============ 25 passed in 5.34s ============
#
# Coverage Report:
# Name                                    Stmts   Miss  Cover
# -----------------------------------------------------------
# services/mcp_client.py                    78      3    96%
# workflows/class_diagram_workflow.py      134      8    94%
# models/diagram.py                         15      0   100%
# -----------------------------------------------------------
# TOTAL                                    227     11    95%
```

---

## ✅ Verification Checklist

Before proceeding to Phase 6, ensure:

- [ ] `tests/conftest.py` created with fixtures
- [ ] `tests/test_mcp_client.py` created (9+ unit tests)
- [ ] `tests/test_class_diagram_workflow.py` created (8+ integration tests)
- [ ] `tests/test_api_e2e.py` created (5+ E2E tests)
- [ ] `pytest.ini` configured
- [ ] `scripts/run-tests.ps1` created
- [ ] All unit tests pass
- [ ] All integration tests pass (with mocks)
- [ ] All E2E tests pass (with services running)
- [ ] Code coverage >90%

---

## 🎯 Commit Time!

```powershell
# Stage test files
git add tests/
git add pytest.ini
git add scripts/run-tests.ps1

# Commit
git commit -m "test: add comprehensive tests for diagram validation integration

Test Coverage:
- Unit tests for MCP client (9 tests)
- Integration tests for LangGraph workflow (8 tests)
- End-to-end API tests (5 tests)
- Total: 22 tests with 95%+ coverage

Test Infrastructure:
- pytest configuration with async support
- Comprehensive fixtures for mocking
- Test markers (unit, integration, e2e, slow)
- Coverage reporting (HTML + terminal)
- Test runner script (run-tests.ps1)

Key Tests:
- Valid diagram validation
- Invalid diagram retry logic
- Max retry handling
- MCP server unavailability
- API error handling
- Health check integration

Refs: #OPS-266"
```

---

## 🐛 Troubleshooting

### Issue: Async tests not running

**Symptom**: `RuntimeError: Event loop is closed`

**Solution**: Ensure `pytest-asyncio` installed and configured

```powershell
pip install pytest-asyncio
```

Add to `pytest.ini`:

```ini
asyncio_mode = auto
```

### Issue: Mocks not working

**Symptom**: Real MCP server called instead of mock

**Debug**:

```python
# Verify patch path is correct
with patch("services.mcp_client.MCPClient"):  # Correct
with patch("mcp_client.MCPClient"):  # Wrong
```

### Issue: E2E tests fail

**Symptom**: Connection refused or timeout

**Solution**: Ensure services are running

```powershell
docker-compose ps  # Check service status
docker-compose logs mcp-server  # Check MCP logs
```

---

## 📚 Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio Guide](https://pytest-asyncio.readthedocs.io/)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

---

**Next Phase**: [06_DEPLOYMENT_VERIFICATION.md](./06_DEPLOYMENT_VERIFICATION.md) →

---

**Phase 5 Complete** ✅  
**Est. Completion Time**: 30-35 minutes  
**Commit**: `test: add comprehensive tests for diagram validation integration`
