# Phase 1: Dependencies Setup

## 🎯 Objective

Install and configure all Python and Node.js dependencies required for NodeJS subprocess-based Mermaid validation.

**Estimated Time**: 20-30 minutes  
**Commit Message**: `feat: add Python & Node.js dependencies for Mermaid validation`

---

## 📦 Dependencies Overview

### Python Packages

| Package          | Version | Purpose                                        | Category |
| ---------------- | ------- | ---------------------------------------------- | -------- |
| `httpx`          | ^0.27.0 | Async HTTP client for subprocess communication | Core     |
| `psutil`         | ^5.9.0  | Process monitoring and management              | Core     |
| `pytest-asyncio` | ^0.23.0 | Async test support                             | Testing  |
| `pytest-mock`    | ^3.12.0 | Mocking utilities                              | Testing  |
| `pytest-timeout` | ^2.2.0  | Test timeout handling                          | Testing  |

### Node.js Packages

| Package                   | Version | Purpose                                   | Category |
| ------------------------- | ------- | ----------------------------------------- | -------- |
| `express`                 | ^4.18.0 | HTTP server framework                     | Core     |
| `@mermaid-js/mermaid-cli` | ^10.6.0 | Official Mermaid validation               | Core     |
| `puppeteer`               | ^21.0.0 | Headless browser (mermaid-cli dependency) | Core     |
| `cors`                    | ^2.8.5  | CORS middleware                           | Core     |
| `helmet`                  | ^7.1.0  | Security headers                          | Security |

---

## 🔍 Deep Dive: Dependency Rationale

### httpx: Modern Async HTTP Client

**Why httpx over requests?**

```python
# Traditional requests (BLOCKING - BAD for FastAPI)
import requests
response = requests.get("http://localhost:3001/health")  # Blocks event loop!

# Modern httpx (NON-BLOCKING - GOOD for FastAPI)
import httpx
async with httpx.AsyncClient() as client:
    response = await client.get("http://localhost:3001/health")  # Async!
```

**Performance Comparison**:

| Metric                  | requests (sync)    | httpx (async)    | Improvement         |
| ----------------------- | ------------------ | ---------------- | ------------------- |
| **Concurrent Requests** | Sequential (1→2→3) | Parallel (1∥2∥3) | 3x faster           |
| **FastAPI Integration** | Blocks workers     | Native async     | ✅ Perfect          |
| **HTTP/2 Support**      | ❌ No              | ✅ Yes           | Modern protocol     |
| **Connection Pooling**  | Manual             | Automatic        | Better resource use |

**Real-world Example**:

```python
# Scenario: 10 validation requests arrive simultaneously

# With requests (sync):
# Request 1: 200ms → Total: 200ms
# Request 2: 200ms → Total: 400ms (waits for #1)
# ...
# Request 10: 200ms → Total: 2000ms (waits for all)

# With httpx (async):
# All 10 requests: ~200ms (parallel processing)
# Total: 200ms for all 10!
```

**API Design**:

```python
import httpx

# Context manager (recommended)
async with httpx.AsyncClient(timeout=10.0) as client:
    response = await client.post(
        "http://localhost:3001/validate",
        json={"code": "graph TD\nA-->B"},
        headers={"Content-Type": "application/json"}
    )
    result = response.json()

# Reusable client (advanced)
class ValidatorClient:
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=10.0,
            limits=httpx.Limits(max_keepalive_connections=5)
        )

    async def validate(self, code: str):
        response = await self.client.post(
            "http://localhost:3001/validate",
            json={"code": code}
        )
        return response.json()

    async def close(self):
        await self.client.aclose()
```

### psutil: Process Monitoring

**Why psutil?**

Standard `os` and `subprocess` modules provide basic process info, but psutil gives:

- ✅ **CPU Usage**: Monitor subprocess resource consumption
- ✅ **Memory Stats**: Detect memory leaks
- ✅ **Process Tree**: Find child processes (puppeteer spawns Chrome)
- ✅ **Cross-platform**: Works on Windows, Linux, macOS

**Usage in Subprocess Manager**:

```python
import psutil
import asyncio

class SubprocessMonitor:
    def __init__(self, process: asyncio.subprocess.Process):
        self.process = process
        self.ps_process = psutil.Process(process.pid)

    def get_metrics(self) -> dict:
        """Get process performance metrics"""
        return {
            "cpu_percent": self.ps_process.cpu_percent(interval=0.1),
            "memory_mb": self.ps_process.memory_info().rss / 1024 / 1024,
            "num_threads": self.ps_process.num_threads(),
            "status": self.ps_process.status(),
            "children": len(self.ps_process.children())  # puppeteer chromium
        }

    def is_healthy(self) -> bool:
        """Check if process is in healthy state"""
        metrics = self.get_metrics()
        return (
            metrics["status"] == "running" and
            metrics["memory_mb"] < 500 and  # < 500MB RAM
            metrics["cpu_percent"] < 80  # < 80% CPU
        )
```

**Health Monitoring Example**:

```python
# Monitor subprocess health every 30 seconds
async def health_monitor(manager: SubprocessManager):
    while True:
        await asyncio.sleep(30)

        metrics = manager.get_metrics()
        logger.info(f"Subprocess metrics: {metrics}")

        if not manager.is_healthy():
            logger.warning("Subprocess unhealthy, restarting...")
            await manager.restart()
```

### @mermaid-js/mermaid-cli: Official Validator

**Why mermaid-cli?**

This is the **official** Mermaid.js command-line tool, maintained by the Mermaid team.

**Features**:

- ✅ Syntax validation (our primary use case)
- ✅ Diagram rendering to PNG/SVG
- ✅ PDF generation
- ✅ Configuration support

**How it works internally**:

```javascript
// mermaid-cli uses Puppeteer + Mermaid.js

const puppeteer = require('puppeteer');
const mermaid = require('mermaid');

async function validate(code) {
  // 1. Launch headless Chrome
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox'],
  });

  // 2. Create page with Mermaid
  const page = await browser.newPage();
  await page.addScriptTag({ path: 'mermaid.min.js' });

  // 3. Try to parse diagram
  const result = await page.evaluate((code) => {
    try {
      mermaid.parse(code); // Validates syntax
      return { valid: true };
    } catch (error) {
      return {
        valid: false,
        errors: [error.message],
        line: error.hash?.line,
      };
    }
  }, code);

  await browser.close();
  return result;
}
```

**Why not alternatives?**

| Alternative                 | Pros                 | Cons                    | Verdict              |
| --------------------------- | -------------------- | ----------------------- | -------------------- |
| **mermaid.js (browser)**    | Lightweight          | Requires DOM/browser    | ❌ Not for backend   |
| **mermaid-isomorphic**      | Server-side          | Outdated, unmaintained  | ❌ Risky             |
| **Custom parser**           | Full control         | Huge maintenance burden | ❌ Reinventing wheel |
| **@mermaid-js/mermaid-cli** | Official, maintained | Puppeteer overhead      | ✅ Best choice       |

### Express.js: Lightweight HTTP Server

**Why Express over alternatives?**

| Framework    | Complexity | Performance | Bundle Size | Verdict       |
| ------------ | ---------- | ----------- | ----------- | ------------- |
| **Express**  | Low        | Fast        | ~1MB        | ✅ Perfect    |
| **Fastify**  | Medium     | Faster      | ~500KB      | Overkill      |
| **Koa**      | Medium     | Fast        | ~500KB      | Unnecessary   |
| **Raw http** | High       | Fastest     | 0KB         | Too low-level |

**Simple Express Server**:

```javascript
// server.js - Minimal validation server
const express = require('express');
const { run } = require('@mermaid-js/mermaid-cli');

const app = express();
app.use(express.json());

// Validation endpoint
app.post('/validate', async (req, res) => {
  const { code } = req.body;

  try {
    // mermaid-cli throws on invalid syntax
    await run(code, 'output.tmp.png', {
      parseMMDOptions: { mermaidConfig: {} },
    });

    res.json({ valid: true, code });
  } catch (error) {
    res.json({
      valid: false,
      code,
      errors: [error.message],
    });
  }
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: Date.now() });
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`Mermaid validator listening on port ${PORT}`);
});
```

---

## 🛠️ Implementation Steps

### Step 1: Activate Virtual Environment

```powershell
# Navigate to ba_copilot_ai directory
cd d:\Do_an_tot_nghiep\ba_copilot_ai

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Verify activation (should show (.venv) in prompt)
# (.venv) PS D:\Do_an_tot_nghiep\ba_copilot_ai>
```

**Verification**:

```powershell
# Confirm Python is from virtual environment
python -c "import sys; print(sys.prefix)"
# Expected output: D:\Do_an_tot_nghiep\ba_copilot_ai\.venv

# Check Python version
python --version
# Expected: Python 3.11.x or higher
```

**Troubleshooting**:

```powershell
# If activation fails with execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# If .venv doesn't exist, create it:
python -m venv .venv

# Then activate:
.\.venv\Scripts\Activate.ps1
```

---

### Step 2: Install Python Dependencies

```powershell
# Install core packages for subprocess management
pip install httpx==0.27.0
pip install psutil==5.9.8

# Install testing packages
pip install pytest-asyncio==0.23.2
pip install pytest-mock==3.12.0
pip install pytest-timeout==2.2.0

# Verify installation
pip list | Select-String -Pattern "httpx|psutil|pytest"
```

**Expected Output**:

```
httpx                   0.27.0
httpx-core              1.0.2
psutil                  5.9.8
pytest                  7.4.0
pytest-asyncio          0.23.2
pytest-cov              4.1.0
pytest-mock             3.12.0
pytest-timeout          2.2.0
```

**Alternative (batch install)**:

```powershell
# Create temporary requirements file
@"
httpx==0.27.0
psutil==5.9.8
pytest-asyncio==0.23.2
pytest-mock==3.12.0
pytest-timeout==2.2.0
"@ | Out-File -FilePath temp_requirements.txt -Encoding utf8

# Install all at once
pip install -r temp_requirements.txt

# Clean up
Remove-Item temp_requirements.txt
```

---

### Step 3: Update requirements.txt

**Manual Update**:

Open `requirements.txt` and add the new dependencies:

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

# Database
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0

# Utilities
python-dotenv>=1.0.0
requests>=2.31.0

# Subprocess Management & Validation (NEW)
httpx>=0.27.0
psutil>=5.9.8

# Testing (UPDATED)
pytest>=7.4.0
pytest-asyncio>=0.23.2
pytest-mock>=3.12.0
pytest-timeout>=2.2.0
pytest-cov>=4.1.0
httpx>=0.24.0
```

**Automated Update**:

```powershell
# Generate from current environment
pip freeze | Out-File -FilePath requirements.txt -Encoding utf8
```

⚠️ **Note**: `pip freeze` includes transitive dependencies (e.g., `httpx-core`, `certifi`). This is verbose but ensures exact reproducibility.

**Best Practice**: Manual editing for readability, `pip freeze` for production deployments.

---

### Step 4: Create Node.js Project Structure

```powershell
# Create directory for Node.js validator
New-Item -ItemType Directory -Path "services\mermaid_validator\nodejs" -Force

# Navigate to nodejs directory
cd services\mermaid_validator\nodejs

# Initialize Node.js project
npm init -y
```

**Expected Output**:

```
Wrote to d:\Do_an_tot_nghiep\ba_copilot_ai\services\mermaid_validator\nodejs\package.json:

{
  "name": "nodejs",
  "version": "1.0.0",
  "description": "",
  "main": "index.js",
  "scripts": {
    "test": "echo \"Error: no test specified\" && exit 1"
  },
  "keywords": [],
  "author": "",
  "license": "ISC"
}
```

---

### Step 5: Install Node.js Dependencies

```powershell
# Still in services/mermaid_validator/nodejs directory

# Install core dependencies
npm install express@4.18.2
npm install @mermaid-js/mermaid-cli@10.6.1
npm install cors@2.8.5
npm install helmet@7.1.0

# Install development dependencies
npm install --save-dev nodemon@3.0.2
```

**Verify Installation**:

```powershell
# Check package.json
Get-Content package.json | Select-String -Pattern "express|mermaid|cors"

# Check node_modules exists
Test-Path node_modules
# Should return: True

# List installed packages
npm list --depth=0
```

**Expected package.json**:

```json
{
  "name": "mermaid-validator",
  "version": "1.0.0",
  "description": "Node.js Mermaid diagram validation service",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js",
    "test": "echo \"Error: no test specified\" && exit 1"
  },
  "keywords": ["mermaid", "validation", "diagrams"],
  "author": "BA Copilot Team",
  "license": "MIT",
  "dependencies": {
    "@mermaid-js/mermaid-cli": "^10.6.1",
    "cors": "^2.8.5",
    "express": "^4.18.2",
    "helmet": "^7.1.0"
  },
  "devDependencies": {
    "nodemon": "^3.0.2"
  }
}
```

---

### Step 6: Configure Package.json Scripts

Update `package.json` with useful scripts:

```powershell
# Navigate to nodejs directory
cd d:\Do_an_tot_nghiep\ba_copilot_ai\services\mermaid_validator\nodejs
```

Edit `package.json`:

```json
{
  "name": "mermaid-validator",
  "version": "1.0.0",
  "description": "Node.js Mermaid diagram validation service for ba_copilot_ai",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js",
    "test": "node test.js",
    "health": "curl http://localhost:3001/health"
  },
  "engines": {
    "node": ">=18.0.0",
    "npm": ">=9.0.0"
  },
  "keywords": ["mermaid", "validation", "diagrams", "uml"],
  "author": "BA Copilot Team",
  "license": "MIT",
  "dependencies": {
    "@mermaid-js/mermaid-cli": "^10.6.1",
    "cors": "^2.8.5",
    "express": "^4.18.2",
    "helmet": "^7.1.0"
  },
  "devDependencies": {
    "nodemon": "^3.0.2"
  }
}
```

**Script Explanations**:

| Script   | Command             | Purpose                      |
| -------- | ------------------- | ---------------------------- |
| `start`  | `node server.js`    | Production server start      |
| `dev`    | `nodemon server.js` | Development with auto-reload |
| `test`   | `node test.js`      | Run basic tests              |
| `health` | `curl ...`          | Quick health check           |

---

### Step 7: Create .gitignore for Node.js

```powershell
# In services/mermaid_validator/nodejs directory

# Create .gitignore
@"
# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Environment
.env
.env.local

# Testing
coverage/
*.log

# OS
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.tmp.*
output.*.png
output.*.svg
"@ | Out-File -FilePath .gitignore -Encoding utf8
```

---

### Step 8: Update Python .env Configuration

```powershell
# Navigate back to ba_copilot_ai root
cd d:\Do_an_tot_nghiep\ba_copilot_ai
```

**Update `.env.example`**:

```bash
# OpenRouter API Configuration
OPEN_ROUTER_API_KEY=your_openrouter_api_key_here

# Database Configuration
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=ba_copilot
DATABASE_URL=postgresql://user:password@db:5432/ba_copilot

# Application Settings
ENV=development
DEBUG=true
LOG_LEVEL=INFO

# Mermaid Validation Subprocess (NEW)
MERMAID_VALIDATOR_ENABLED=true
MERMAID_VALIDATOR_PORT=3001
MERMAID_VALIDATOR_HOST=localhost
MERMAID_VALIDATOR_TIMEOUT=10
MERMAID_VALIDATOR_MAX_RETRIES=3
MERMAID_VALIDATOR_STARTUP_TIMEOUT=30
```

**Update your local `.env`**:

```powershell
# Add to existing .env file
@"

# Mermaid Validation Subprocess
MERMAID_VALIDATOR_ENABLED=true
MERMAID_VALIDATOR_PORT=3001
MERMAID_VALIDATOR_HOST=localhost
MERMAID_VALIDATOR_TIMEOUT=10
MERMAID_VALIDATOR_MAX_RETRIES=3
MERMAID_VALIDATOR_STARTUP_TIMEOUT=30
"@ | Add-Content -Path .env -Encoding utf8
```

---

### Step 9: Create Python Services Directory Structure

```powershell
# Create services/mermaid_validator Python package
New-Item -ItemType Directory -Path "services\mermaid_validator" -Force

# Create __init__.py to make it a package
New-Item -ItemType File -Path "services\mermaid_validator\__init__.py" -Force

# Create placeholder files for next phases
New-Item -ItemType File -Path "services\mermaid_validator\subprocess_manager.py" -Force
New-Item -ItemType File -Path "services\mermaid_validator\client.py" -Force
New-Item -ItemType File -Path "services\mermaid_validator\exceptions.py" -Force
```

**Initial `__init__.py`**:

```python
"""
Mermaid Validator Service

Node.js subprocess-based Mermaid diagram validation.

Components:
    - subprocess_manager: Lifecycle management for Node.js validator
    - client: HTTP client for validation requests
    - exceptions: Custom exception classes
"""

from .exceptions import (
    MermaidValidatorError,
    SubprocessStartupError,
    SubprocessUnavailable,
    ValidationTimeout
)

__all__ = [
    "MermaidValidatorError",
    "SubprocessStartupError",
    "SubprocessUnavailable",
    "ValidationTimeout"
]
```

**Initial `exceptions.py`**:

```python
"""
Custom exceptions for Mermaid validation service.
"""

class MermaidValidatorError(Exception):
    """Base exception for Mermaid validator errors"""
    pass


class SubprocessStartupError(MermaidValidatorError):
    """Raised when Node.js subprocess fails to start"""
    pass


class SubprocessUnavailable(MermaidValidatorError):
    """Raised when subprocess is not running or unreachable"""
    pass


class ValidationTimeout(MermaidValidatorError):
    """Raised when validation request times out"""
    def __init__(self, message: str, timeout: float):
        super().__init__(message)
        self.timeout = timeout
```

---

### Step 10: Verify Installation

Create a verification script:

**File**: `verify_setup.py` (temporary, in ba_copilot_ai root)

```python
"""
Quick verification script for dependency installation.
Run: python verify_setup.py
"""

import sys
import os
import subprocess
from pathlib import Path

def check_python_packages():
    """Verify Python packages are installed"""
    print("🔍 Checking Python packages...")

    required_packages = {
        "httpx": "0.27.0",
        "psutil": "5.9",
        "pytest-asyncio": "0.23",
        "pytest-mock": "3.12"
    }

    all_ok = True
    for package, min_version in required_packages.items():
        try:
            if package == "pytest-asyncio":
                import pytest_asyncio
                version = pytest_asyncio.__version__
            elif package == "pytest-mock":
                import pytest_mock
                version = pytest_mock.__version__
            elif package == "httpx":
                import httpx
                version = httpx.__version__
            elif package == "psutil":
                import psutil
                version = psutil.__version__

            print(f"  ✓ {package}: {version}")
        except ImportError:
            print(f"  ✗ {package}: NOT INSTALLED")
            all_ok = False

    return all_ok


def check_nodejs_setup():
    """Verify Node.js and packages are installed"""
    print("\n🔍 Checking Node.js setup...")

    # Check Node.js
    try:
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        node_version = result.stdout.strip()
        print(f"  ✓ Node.js: {node_version}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("  ✗ Node.js: NOT INSTALLED")
        return False

    # Check npm
    try:
        result = subprocess.run(
            ["npm", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        npm_version = result.stdout.strip()
        print(f"  ✓ npm: {npm_version}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("  ✗ npm: NOT INSTALLED")
        return False

    # Check package.json exists
    package_json = Path("services/mermaid_validator/nodejs/package.json")
    if package_json.exists():
        print(f"  ✓ package.json: Found")
    else:
        print(f"  ✗ package.json: NOT FOUND")
        return False

    # Check node_modules exists
    node_modules = Path("services/mermaid_validator/nodejs/node_modules")
    if node_modules.exists():
        print(f"  ✓ node_modules: Installed")
    else:
        print(f"  ✗ node_modules: NOT INSTALLED")
        print("    Run: cd services/mermaid_validator/nodejs && npm install")
        return False

    return True


def check_directory_structure():
    """Verify directory structure is correct"""
    print("\n🔍 Checking directory structure...")

    required_dirs = [
        "services/mermaid_validator",
        "services/mermaid_validator/nodejs"
    ]

    required_files = [
        "services/mermaid_validator/__init__.py",
        "services/mermaid_validator/exceptions.py",
        "services/mermaid_validator/nodejs/package.json"
    ]

    all_ok = True

    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"  ✓ {dir_path}/")
        else:
            print(f"  ✗ {dir_path}/ - NOT FOUND")
            all_ok = False

    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} - NOT FOUND")
            all_ok = False

    return all_ok


def check_environment():
    """Verify environment variables"""
    print("\n🔍 Checking environment configuration...")

    from dotenv import load_dotenv
    load_dotenv()

    required_vars = [
        "MERMAID_VALIDATOR_ENABLED",
        "MERMAID_VALIDATOR_PORT",
        "MERMAID_VALIDATOR_HOST"
    ]

    all_ok = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✓ {var}: {value}")
        else:
            print(f"  ✗ {var}: NOT SET")
            all_ok = False

    return all_ok


def main():
    print("=" * 60)
    print("  Mermaid Validation Setup Verification")
    print("=" * 60)

    checks = [
        ("Python Packages", check_python_packages),
        ("Node.js Setup", check_nodejs_setup),
        ("Directory Structure", check_directory_structure),
        ("Environment Variables", check_environment)
    ]

    results = []
    for name, check_func in checks:
        result = check_func()
        results.append((name, result))

    print("\n" + "=" * 60)
    print("  Summary")
    print("=" * 60)

    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}  {name}")
        if not result:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n🎉 All checks passed! Ready for Phase 2.")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please fix issues before continuing.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

**Run verification**:

```powershell
python verify_setup.py
```

**Expected Output**:

```
============================================================
  Mermaid Validation Setup Verification
============================================================
🔍 Checking Python packages...
  ✓ httpx: 0.27.0
  ✓ psutil: 5.9.8
  ✓ pytest-asyncio: 0.23.2
  ✓ pytest-mock: 3.12.0

🔍 Checking Node.js setup...
  ✓ Node.js: v18.19.0
  ✓ npm: 10.2.3
  ✓ package.json: Found
  ✓ node_modules: Installed

🔍 Checking directory structure...
  ✓ services/mermaid_validator/
  ✓ services/mermaid_validator/nodejs/
  ✓ services/mermaid_validator/__init__.py
  ✓ services/mermaid_validator/exceptions.py
  ✓ services/mermaid_validator/nodejs/package.json

🔍 Checking environment configuration...
  ✓ MERMAID_VALIDATOR_ENABLED: true
  ✓ MERMAID_VALIDATOR_PORT: 3001
  ✓ MERMAID_VALIDATOR_HOST: localhost

============================================================
  Summary
============================================================
✅ PASS  Python Packages
✅ PASS  Node.js Setup
✅ PASS  Directory Structure
✅ PASS  Environment Variables
============================================================

🎉 All checks passed! Ready for Phase 2.
```

---

## ✅ Verification Checklist

Before proceeding to Phase 2, ensure:

- [ ] Virtual environment activated
- [ ] All Python packages installed (`httpx`, `psutil`, pytest extensions)
- [ ] `requirements.txt` updated with new dependencies
- [ ] Node.js 18+ and npm installed
- [ ] `services/mermaid_validator/nodejs/` directory created
- [ ] `package.json` created with correct dependencies
- [ ] `node_modules/` populated (npm install completed)
- [ ] Environment variables added to `.env` and `.env.example`
- [ ] Directory structure matches specification
- [ ] `verify_setup.py` script passes all checks

---

## 🎯 Commit Time!

```powershell
# Stage all changes
git add requirements.txt
git add .env.example
git add services/mermaid_validator/
git add verify_setup.py

# Commit with descriptive message
git commit -m "feat: add Python & Node.js dependencies for Mermaid validation

- Install httpx 0.27.0 for async HTTP communication with subprocess
- Add psutil 5.9.8 for process monitoring and health checks
- Add pytest extensions (asyncio, mock, timeout) for testing
- Create Node.js project with Express + @mermaid-js/mermaid-cli
- Set up mermaid_validator service package structure
- Add environment configuration for validator subprocess
- Create verification script for setup validation

Dependencies:
  Python: httpx, psutil, pytest-asyncio, pytest-mock, pytest-timeout
  Node.js: express, @mermaid-js/mermaid-cli, cors, helmet

Refs: #OPS-317"
```

---

## 🐛 Troubleshooting

### Issue: pip install fails with SSL error

**Symptom**:

```
SSL: CERTIFICATE_VERIFY_FAILED
```

**Solution**:

```powershell
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org httpx psutil
```

### Issue: npm install fails with network error

**Symptom**:

```
ENOTFOUND registry.npmjs.org
```

**Solution**:

```powershell
# Check npm registry
npm config get registry
# Should be: https://registry.npmjs.org/

# If not, set it:
npm config set registry https://registry.npmjs.org/

# Retry install
npm install
```

### Issue: @mermaid-js/mermaid-cli installation hangs

**Symptom**:

```
Installing puppeteer... (hangs)
```

**Solution**:

```powershell
# Puppeteer downloads Chromium (large). Be patient or:

# Skip Chromium download, use system Chrome
$env:PUPPETEER_SKIP_CHROMIUM_DOWNLOAD="true"
npm install @mermaid-js/mermaid-cli

# Note: You'll need to configure puppeteer to use system Chrome later
```

### Issue: Node.js not found

**Symptom**:

```
node: The term 'node' is not recognized
```

**Solution**:

```powershell
# Install Node.js from https://nodejs.org/
# Download LTS version (18.x or 20.x)

# After install, restart PowerShell and verify:
node --version
npm --version
```

### Issue: Virtual environment not activating

**Symptom**:

```
Activate.ps1 cannot be loaded because running scripts is disabled
```

**Solution**:

```powershell
# Allow script execution for current user
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Retry activation
.\.venv\Scripts\Activate.ps1
```

---

## 📚 Additional Resources

### Python Resources

- [httpx Documentation](https://www.python-httpx.org/)
- [psutil Documentation](https://psutil.readthedocs.io/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)

### Node.js Resources

- [Express.js Guide](https://expressjs.com/en/guide/routing.html)
- [@mermaid-js/mermaid-cli](https://github.com/mermaid-js/mermaid-cli)
- [npm Documentation](https://docs.npmjs.com/)

### Environment Management

- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [Node.js Environment Variables](https://nodejs.org/api/process.html#processenv)

---

**Next Phase**: [02_NODEJS_VALIDATOR_SERVICE.md](./02_NODEJS_VALIDATOR_SERVICE.md) →

---

**Phase 1 Complete** ✅  
**Est. Completion Time**: 20-30 minutes  
**Commit**: `feat: add Python & Node.js dependencies for Mermaid validation`
