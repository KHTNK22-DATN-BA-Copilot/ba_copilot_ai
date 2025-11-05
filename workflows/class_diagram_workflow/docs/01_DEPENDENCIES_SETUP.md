# Phase 1: Dependencies Setup

## 🎯 Objective

Install and configure all Python and Node.js dependencies required for MCP integration and Mermaid validation.

**Estimated Time**: 15-20 minutes  
**Commit Message**: `feat: add MCP client dependencies and Python packages`

---

## 📦 Dependencies Overview

### Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| `httpx` | ^0.27.0 | Async HTTP client for MCP server communication |
| `pytest-asyncio` | ^0.23.0 | Async support for pytest |
| `pytest-mock` | ^3.12.0 | Mocking utilities for tests |
| `pytest-cov` | ^4.1.0 | Code coverage reporting |

### Node.js Packages (Global)

| Package | Version | Purpose |
|---------|---------|---------|
| `@rtuin/mcp-mermaid-validator` | Latest | MCP server for Mermaid validation |

---

## 🔍 Deep Dive: Why These Dependencies?

### httpx vs requests

**Decision Rationale**: Use `httpx` over `requests`

| Aspect | requests | httpx | Winner |
|--------|----------|-------|--------|
| **Async Support** | ❌ No | ✅ Native | httpx |
| **HTTP/2** | ❌ No | ✅ Yes | httpx |
| **API Design** | Good | Better (modern) | httpx |
| **Performance** | Baseline | 10-30% faster | httpx |
| **Maturity** | Very mature | Mature enough | Tie |

**Code Comparison**:
```python
# Synchronous (requests) - blocks FastAPI workers
import requests
response = requests.post(url, json=data)  # Blocks!

# Asynchronous (httpx) - non-blocking
import httpx
async with httpx.AsyncClient() as client:
    response = await client.post(url, json=data)  # Async!
```

**Why Async Matters**:
- FastAPI is async-first framework
- Validation calls shouldn't block other requests
- Better resource utilization under load
- Example: 10 concurrent requests
  - **Sync**: 10 × 200ms = 2000ms total
  - **Async**: max(200ms) = 200ms total

### pytest-asyncio: Testing Async Code

**Problem**: Standard pytest can't test async functions

```python
# This WON'T work with standard pytest
async def test_validate_mermaid():
    result = await validate_mermaid("graph TD\nA-->B")
    assert result["valid"] is True
```

**Solution**: `pytest-asyncio` decorator

```python
import pytest

@pytest.mark.asyncio  # Magic decorator!
async def test_validate_mermaid():
    result = await validate_mermaid("graph TD\nA-->B")
    assert result["valid"] is True
```

**Best Practices**:
```python
# Configure in pytest.ini
[pytest]
asyncio_mode = auto  # Automatically detect async tests

# Or per-test
@pytest.mark.asyncio
async def test_something():
    ...
```

### pytest-mock: Mocking MCP Server

**Why Mock?**
- **Unit Tests**: Test validation logic without MCP server running
- **CI/CD**: Tests run without external dependencies
- **Speed**: Mocked calls are instant
- **Reliability**: No network flakiness

**Mock Strategy**:
```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_validation_success(mocker):
    # Mock httpx POST request
    mock_post = mocker.patch("httpx.AsyncClient.post")
    mock_post.return_value.json.return_value = {
        "jsonrpc": "2.0",
        "result": {"valid": True},
        "id": 1
    }
    
    # Test validation logic
    result = await validate_mermaid("graph TD\nA-->B")
    assert result["valid"] is True
    mock_post.assert_called_once()
```

### pytest-cov: Coverage Reporting

**Why Coverage Matters**:
- **Quality Gate**: Enforce minimum coverage (e.g., 90%)
- **Find Gaps**: Identify untested code paths
- **Refactoring Safety**: High coverage = safe to refactor

**Coverage Strategy**:
```bash
# Run tests with coverage
pytest --cov=workflows --cov=services --cov-report=html --cov-report=term

# Output example:
# Name                              Stmts   Miss  Cover
# ------------------------------------------------------
# services/mcp_client.py              45      2    96%
# workflows/class_diagram_workflow    67      5    93%
# ------------------------------------------------------
# TOTAL                              112      7    94%
```

---

## 🛠️ Implementation Steps

### Step 1: Activate Virtual Environment

```powershell
# Navigate to project directory
cd d:\Do_an_tot_nghiep\ba_copilot_ai

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Verify activation (should show .venv in prompt)
# (.venv) PS D:\Do_an_tot_nghiep\ba_copilot_ai>
```

**Verification**:
```powershell
# Check Python is from venv
python -c "import sys; print(sys.prefix)"
# Should output: D:\Do_an_tot_nghiep\ba_copilot_ai\.venv
```

**Troubleshooting**:
```powershell
# If execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# If venv doesn't exist:
python -m venv .venv
```

---

### Step 2: Install Python Dependencies

```powershell
# Install new packages
pip install httpx==0.27.0
pip install pytest-asyncio==0.23.0
pip install pytest-mock==3.12.0
pip install pytest-cov==4.1.0

# Verify installation
pip list | Select-String -Pattern "httpx|pytest"
```

**Expected Output**:
```
httpx                   0.27.0
pytest-asyncio          0.23.0
pytest-cov              4.1.0
pytest-mock             3.12.0
```

**Alternative (batch install)**:
```powershell
# Create temporary requirements file
@"
httpx==0.27.0
pytest-asyncio==0.23.0
pytest-mock==3.12.0
pytest-cov==4.1.0
"@ | Out-File -FilePath temp_requirements.txt -Encoding utf8

# Install all at once
pip install -r temp_requirements.txt

# Remove temp file
Remove-Item temp_requirements.txt
```

---

### Step 3: Update requirements.txt

**Manual Method**:

Open `requirements.txt` and add the following lines after the existing dependencies:

```txt
# FastAPI and server
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.5.0
pydantic-settings>=2.1.0

# LangChain and LangGraph
langchain>=0.1.16
langgraph>=0.0.52

# OpenAI (for OpenRouter)
openai>=1.0.0

# Database (if needed)
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0

# Utilities
python-dotenv>=1.0.0
requests>=2.31.0

# MCP Integration (NEW)
httpx>=0.27.0

# Testing (NEW)
pytest>=7.4.0
pytest-asyncio>=0.23.0
pytest-mock>=3.12.0
pytest-cov>=4.1.0
```

**Automated Method**:

```powershell
# Freeze current environment to requirements.txt
pip freeze > requirements.txt
```

**⚠️ Warning**: `pip freeze` includes ALL packages (including transitive dependencies). This creates a verbose file but ensures reproducibility.

**Best Practice**: Use `pip freeze` for deployment, manual editing for readability.

---

### Step 4: Install Node.js MCP Server (Global)

**Why Global Installation?**
- MCP server runs as standalone process
- Not part of Python application
- Needs to be accessible from Docker container

```powershell
# Install MCP Mermaid Validator globally
npx -y @rtuin/mcp-mermaid-validator

# This downloads and caches the package
# -y flag auto-accepts prompts
```

**Verification**:
```powershell
# Test MCP server starts
npx @rtuin/mcp-mermaid-validator

# Expected output (server starts):
# MCP Mermaid Validator running on http://localhost:3000
# Press Ctrl+C to stop
```

**Understanding npx**:
- `npx`: Node Package Execute (runs packages without global install)
- `-y`: Auto-accept installation prompts
- Downloads to npm cache: `~\AppData\Local\npm-cache`

**Alternative (Traditional npm install)**:
```powershell
# Global install (if you prefer)
npm install -g @rtuin/mcp-mermaid-validator

# Then run directly
mcp-mermaid-validator
```

---

### Step 5: Test MCP Server Locally

**Terminal 1 - Start MCP Server**:
```powershell
npx @rtuin/mcp-mermaid-validator

# Should output:
# Server listening on http://localhost:3000
```

**Terminal 2 - Test with curl**:
```powershell
# Test validation endpoint
$body = @{
    jsonrpc = "2.0"
    method = "tools/call"
    params = @{
        name = "validate_mermaid"
        arguments = @{
            code = "graph TD`nA-->B"
        }
    }
    id = 1
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Uri "http://localhost:3000" `
                  -Method Post `
                  -Body $body `
                  -ContentType "application/json"
```

**Expected Response**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Valid Mermaid diagram"
      }
    ]
  },
  "id": 1
}
```

**Test Invalid Mermaid**:
```powershell
$body = @{
    jsonrpc = "2.0"
    method = "tools/call"
    params = @{
        name = "validate_mermaid"
        arguments = @{
            code = "graph TD`nA--INVALID-->B"
        }
    }
    id = 1
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Uri "http://localhost:3000" `
                  -Method Post `
                  -Body $body `
                  -ContentType "application/json"
```

**Expected Error Response**:
```json
{
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
```

---

### Step 6: Create MCP Client Service (Skeleton)

Create the foundational service that will communicate with MCP server.

**File**: `services/mcp_client.py`

```python
"""
MCP Client Service for Mermaid Validation

This service provides an async interface to communicate with the
MCP Mermaid Validator server using JSON-RPC 2.0 protocol.

Architecture:
    FastAPI (Python) --[HTTP/JSON-RPC]--> MCP Server (Node.js)

References:
    - MCP Spec: https://spec.modelcontextprotocol.io/
    - JSON-RPC 2.0: https://www.jsonrpc.org/specification
"""

import httpx
import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Configuration from environment
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:3000")
MCP_TIMEOUT = int(os.getenv("MCP_TIMEOUT", "10"))  # seconds


class MCPClientError(Exception):
    """Base exception for MCP client errors"""
    pass


class MCPServerUnavailable(MCPClientError):
    """Raised when MCP server is not reachable"""
    pass


class MCPValidationError(MCPClientError):
    """Raised when Mermaid validation fails"""
    def __init__(self, message: str, errors: Optional[list] = None):
        super().__init__(message)
        self.errors = errors or []


class MCPClient:
    """
    Asynchronous client for MCP Mermaid Validator server.
    
    Usage:
        async with MCPClient() as client:
            result = await client.validate_mermaid("graph TD\\nA-->B")
            if result["valid"]:
                print("Valid diagram!")
    
    Configuration:
        - MCP_SERVER_URL: URL of MCP server (default: http://localhost:3000)
        - MCP_TIMEOUT: Request timeout in seconds (default: 10)
    """
    
    def __init__(self, base_url: Optional[str] = None, timeout: Optional[int] = None):
        """
        Initialize MCP client.
        
        Args:
            base_url: Override MCP server URL
            timeout: Override request timeout
        """
        self.base_url = base_url or MCP_SERVER_URL
        self.timeout = timeout or MCP_TIMEOUT
        self._client: Optional[httpx.AsyncClient] = None
        self._request_id = 0
    
    async def __aenter__(self):
        """Async context manager entry"""
        self._client = httpx.AsyncClient(
            timeout=self.timeout,
            headers={"Content-Type": "application/json"}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self._client:
            await self._client.aclose()
    
    def _get_request_id(self) -> int:
        """Generate unique request ID for JSON-RPC"""
        self._request_id += 1
        return self._request_id
    
    async def validate_mermaid(self, code: str) -> Dict[str, Any]:
        """
        Validate Mermaid diagram syntax.
        
        Args:
            code: Mermaid diagram code to validate
            
        Returns:
            Dict with validation result:
                {
                    "valid": bool,
                    "code": str,  # Original code
                    "errors": list[str],  # Empty if valid
                }
        
        Raises:
            MCPServerUnavailable: If server is not reachable
            MCPValidationError: If validation fails
            
        Example:
            result = await client.validate_mermaid("graph TD\\nA-->B")
            if result["valid"]:
                print("Valid!")
            else:
                print(f"Errors: {result['errors']}")
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use 'async with MCPClient()' context manager.")
        
        # Construct JSON-RPC 2.0 request
        request_payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "validate_mermaid",
                "arguments": {
                    "code": code
                }
            },
            "id": self._get_request_id()
        }
        
        logger.debug(f"Sending validation request to {self.base_url}")
        
        try:
            response = await self._client.post(
                self.base_url,
                json=request_payload
            )
            response.raise_for_status()
            data = response.json()
            
            # Handle JSON-RPC error response
            if "error" in data:
                error = data["error"]
                error_message = error.get("message", "Unknown error")
                error_data = error.get("data", {})
                errors = error_data.get("errors", [error_message])
                
                logger.warning(f"Validation failed: {error_message}")
                return {
                    "valid": False,
                    "code": code,
                    "errors": errors
                }
            
            # Handle success response
            result = data.get("result", {})
            content = result.get("content", [])
            
            # Check if validation passed
            valid = any(
                item.get("type") == "text" and "valid" in item.get("text", "").lower()
                for item in content
            )
            
            logger.info(f"Validation successful: valid={valid}")
            return {
                "valid": valid,
                "code": code,
                "errors": []
            }
            
        except httpx.TimeoutException as e:
            logger.error(f"MCP server timeout: {e}")
            raise MCPServerUnavailable(f"MCP server timeout after {self.timeout}s") from e
        
        except httpx.ConnectError as e:
            logger.error(f"Cannot connect to MCP server: {e}")
            raise MCPServerUnavailable(f"Cannot connect to MCP server at {self.base_url}") from e
        
        except Exception as e:
            logger.error(f"Unexpected error during validation: {e}")
            raise MCPClientError(f"Validation error: {str(e)}") from e
    
    async def health_check(self) -> bool:
        """
        Check if MCP server is healthy and responding.
        
        Returns:
            True if server is healthy, False otherwise
        """
        try:
            # Simple validation test
            result = await self.validate_mermaid("graph TD\nA-->B")
            return result["valid"]
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


# Convenience function for simple use cases
async def validate_mermaid_code(code: str) -> Dict[str, Any]:
    """
    Standalone function to validate Mermaid code.
    
    Args:
        code: Mermaid diagram code
        
    Returns:
        Validation result dictionary
        
    Example:
        result = await validate_mermaid_code("graph TD\\nA-->B")
    """
    async with MCPClient() as client:
        return await client.validate_mermaid(code)
```

**Create the file**:
```powershell
# Create services directory if not exists
New-Item -ItemType Directory -Path "services" -Force

# Create __init__.py
New-Item -ItemType File -Path "services\__init__.py" -Force
```

---

### Step 7: Update Environment Configuration

**File**: `.env.example`

Add MCP server configuration:

```bash
# OpenRouter API Configuration
OPEN_ROUTER_API_KEY=your_openrouter_api_key_here

# Database Configuration (if needed)
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=ba_copilot
DATABASE_URL=postgresql://user:password@db:5432/ba_copilot

# Application Settings
ENV=development
DEBUG=true
LOG_LEVEL=INFO

# MCP Server Configuration (NEW)
MCP_SERVER_URL=http://localhost:3000
MCP_TIMEOUT=10
```

**File**: `.env` (your local copy)

Update your local `.env` file with the same MCP settings.

---

### Step 8: Verify Installation

Create a simple test script to verify everything works:

**File**: `test_setup.py` (temporary, delete after verification)

```python
"""
Quick verification script for MCP setup.
Run: python test_setup.py
"""

import asyncio
import sys

async def verify_setup():
    print("🔍 Verifying MCP Integration Setup...")
    print()
    
    # Test 1: Import dependencies
    print("✓ Test 1: Importing dependencies")
    try:
        import httpx
        import pytest
        print(f"  - httpx version: {httpx.__version__}")
        print(f"  - pytest version: {pytest.__version__}")
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False
    
    # Test 2: Import MCP client
    print("\n✓ Test 2: Importing MCP client")
    try:
        sys.path.append(".")
        from services.mcp_client import MCPClient, validate_mermaid_code
        print("  - MCPClient imported successfully")
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False
    
    # Test 3: MCP server connection
    print("\n✓ Test 3: Testing MCP server connection")
    print("  ⚠ Make sure MCP server is running: npx @rtuin/mcp-mermaid-validator")
    
    try:
        result = await validate_mermaid_code("graph TD\nA-->B")
        if result["valid"]:
            print("  - MCP server responded successfully")
            print(f"  - Validation result: {result}")
        else:
            print(f"  ⚠ Unexpected validation result: {result}")
    except Exception as e:
        print(f"  ✗ MCP server connection failed: {e}")
        print("  💡 Start MCP server: npx @rtuin/mcp-mermaid-validator")
        return False
    
    print("\n" + "="*50)
    print("✅ All setup verification tests passed!")
    print("="*50)
    return True

if __name__ == "__main__":
    result = asyncio.run(verify_setup())
    sys.exit(0 if result else 1)
```

**Run verification**:
```powershell
# Terminal 1: Start MCP server
npx @rtuin/mcp-mermaid-validator

# Terminal 2: Run verification
python test_setup.py
```

**Expected Output**:
```
🔍 Verifying MCP Integration Setup...

✓ Test 1: Importing dependencies
  - httpx version: 0.27.0
  - pytest version: 7.4.3

✓ Test 2: Importing MCP client
  - MCPClient imported successfully

✓ Test 3: Testing MCP server connection
  ⚠ Make sure MCP server is running: npx @rtuin/mcp-mermaid-validator
  - MCP server responded successfully
  - Validation result: {'valid': True, 'code': 'graph TD\nA-->B', 'errors': []}

==================================================
✅ All setup verification tests passed!
==================================================
```

---

## ✅ Verification Checklist

Before proceeding to Phase 2, ensure:

- [ ] Virtual environment activated
- [ ] All Python packages installed (`pip list` shows httpx, pytest-*)
- [ ] `requirements.txt` updated with new dependencies
- [ ] MCP server installs and runs (`npx @rtuin/mcp-mermaid-validator`)
- [ ] MCP server responds to curl/Invoke-RestMethod test
- [ ] `services/mcp_client.py` created with skeleton code
- [ ] `.env` and `.env.example` updated with MCP_SERVER_URL
- [ ] `test_setup.py` runs successfully

---

## 🎯 Commit Time!

```powershell
# Stage changes
git add requirements.txt
git add services/mcp_client.py
git add .env.example

# Commit with descriptive message
git commit -m "feat: add MCP client dependencies and Python packages

- Install httpx 0.27.0 for async HTTP communication
- Add pytest-asyncio, pytest-mock, pytest-cov for testing
- Create MCPClient service skeleton
- Update environment configuration for MCP server
- Add comprehensive error handling and logging

Refs: #OPS-266"

# Verification commit message follows Conventional Commits:
# feat: new feature
# Descriptive body with bullet points
# Refs: issue tracker reference
```

---

## 🐛 Troubleshooting

### Issue: `pip install` fails with SSL error

**Symptom**:
```
SSL: CERTIFICATE_VERIFY_FAILED
```

**Solution**:
```powershell
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org httpx
```

### Issue: Virtual environment not activating

**Symptom**:
```
Activate.ps1 cannot be loaded because running scripts is disabled
```

**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: `npx` command not found

**Symptom**:
```
npx: The term 'npx' is not recognized
```

**Solution**:
```powershell
# Install Node.js from https://nodejs.org/
# Verify installation
node --version
npm --version
npx --version
```

### Issue: MCP server won't start

**Symptom**:
```
Error: Cannot find module '@rtuin/mcp-mermaid-validator'
```

**Solution**:
```powershell
# Clear npm cache
npm cache clean --force

# Reinstall
npx -y @rtuin/mcp-mermaid-validator
```

### Issue: Port 3000 already in use

**Symptom**:
```
Error: listen EADDRINUSE: address already in use :::3000
```

**Solution**:
```powershell
# Find process using port 3000
Get-Process -Id (Get-NetTCPConnection -LocalPort 3000).OwningProcess

# Kill the process (replace PID)
Stop-Process -Id <PID> -Force

# Or use different port (configure in Phase 2)
```

---

## 📚 Additional Resources

- [httpx Documentation](https://www.python-httpx.org/)
- [pytest-asyncio Guide](https://pytest-asyncio.readthedocs.io/)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)
- [Python Async/Await Tutorial](https://realpython.com/async-io-python/)

---

**Next Phase**: [02_MCP_SERVER_SETUP.md](./02_MCP_SERVER_SETUP.md) →

---

**Phase 1 Complete** ✅  
**Est. Completion Time**: 15-20 minutes  
**Commit**: `feat: add MCP client dependencies and Python packages`
