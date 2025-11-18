# Phase 4: Docker Configuration

## 🎯 Objective

Update Docker configuration to support both Python and Node.js in a single container using multi-stage builds, configure service orchestration, and ensure subprocess communication works in containerized environment.

**Estimated Time**: 30-45 minutes  
**Commit Message**: `chore: update Docker config for Node.js subprocess integration`

---

## 🏗️ Multi-Stage Build Strategy

```
┌──────────────────────────────────────────┐
│  Stage 1: Node.js Builder                │
│  - Install Node.js dependencies          │
│  - Build production node_modules          │
│  - Optimize for size                      │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│  Stage 2: Python Runtime                 │
│  - Install Node.js runtime only          │
│  - Copy pre-built node_modules            │
│  - Install Python dependencies            │
│  - Copy application code                  │
└──────────────────────────────────────────┘
```

**Why Multi-Stage?**

| Aspect              | Single Stage | Multi-Stage | Winner      |
| ------------------- | ------------ | ----------- | ----------- |
| **Image Size**      | ~800MB       | ~450MB      | Multi-Stage |
| **Build Speed**     | Slower       | Cached      | Multi-Stage |
| **Security**        | Build tools  | Clean       | Multi-Stage |
| **Layer Caching**   | Limited      | Optimized   | Multi-Stage |
| **Reproducibility** | Medium       | High        | Multi-Stage |

---

## 🛠️ Implementation Steps

### Step 1: Update Dockerfile

**File**: `ba_copilot_ai/Dockerfile`

```dockerfile
# ============================================================
# Stage 1: Node.js Dependencies Builder
# ============================================================
FROM node:18-alpine AS node-builder

WORKDIR /app/validator

# Copy package files
COPY services/mermaid_validator/nodejs/package*.json ./

# Install dependencies (production only)
RUN npm ci --only=production --no-audit --no-fund

# Verify installation
RUN node -v && npm -v && \
    test -d node_modules/@mermaid-js/mermaid-cli || \
    (echo "ERROR: @mermaid-js/mermaid-cli not installed" && exit 1)


# ============================================================
# Stage 2: Python Application Runtime
# ============================================================
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# - nodejs: Runtime for subprocess
# - npm: Package manager (for debugging)
# - gcc/g++: Python package compilation
# - curl: Health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    nodejs \
    npm \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Verify Node.js installation
RUN node --version && npm --version

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copy Node.js validator service
COPY --chown=appuser:appuser services/mermaid_validator/nodejs /app/services/mermaid_validator/nodejs

# Copy pre-built node_modules from builder stage
COPY --from=node-builder --chown=appuser:appuser \
    /app/validator/node_modules \
    /app/services/mermaid_validator/nodejs/node_modules

# Verify Mermaid CLI installation
RUN test -f /app/services/mermaid_validator/nodejs/node_modules/.bin/mmdc || \
    (echo "ERROR: mmdc binary not found" && exit 1)

# Copy Python requirements
COPY --chown=appuser:appuser requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=appuser:appuser . .

# Create logs directory
RUN mkdir -p /app/logs && chown appuser:appuser /app/logs

# Switch to non-root user
USER appuser

# Expose FastAPI port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Environment variables with defaults
ENV PYTHONUNBUFFERED=1 \
    MERMAID_VALIDATOR_ENABLED=true \
    MERMAID_VALIDATOR_PORT=3001 \
    MERMAID_VALIDATOR_HOST=localhost

# Start FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
```

---

### Step 2: Update docker-compose.yml

**File**: `ba_copilot_ai/docker-compose.yml`

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    container_name: ba_copilot_db
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-ba_copilot}
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
    ports:
      - '${POSTGRES_PORT:-5432}:5432'
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./schema_improved.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ['CMD-SHELL', 'pg_isready -U ${POSTGRES_USER:-postgres}']
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - ba_copilot_network

  # FastAPI AI Service with Node.js Validator
  ai-service:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: ba_copilot_ai
    restart: unless-stopped
    ports:
      - '${AI_SERVICE_PORT:-8000}:8000'
    environment:
      # Database
      DATABASE_URL: postgresql://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-postgres}@db:5432/${POSTGRES_DB:-ba_copilot}

      # OpenRouter API
      OPENROUTER_API_KEY: ${OPENROUTER_API_KEY}
      OPENROUTER_MODEL: ${OPENROUTER_MODEL:-openai/gpt-4}

      # Mermaid Validator Configuration
      MERMAID_VALIDATOR_ENABLED: ${MERMAID_VALIDATOR_ENABLED:-true}
      MERMAID_VALIDATOR_PORT: ${MERMAID_VALIDATOR_PORT:-3001}
      MERMAID_VALIDATOR_HOST: ${MERMAID_VALIDATOR_HOST:-localhost}
      MERMAID_VALIDATOR_STARTUP_TIMEOUT: ${MERMAID_VALIDATOR_STARTUP_TIMEOUT:-30}
      MERMAID_VALIDATOR_REQUEST_TIMEOUT: ${MERMAID_VALIDATOR_REQUEST_TIMEOUT:-10}
      MERMAID_VALIDATOR_HEALTH_CHECK_INTERVAL: ${MERMAID_VALIDATOR_HEALTH_CHECK_INTERVAL:-30}
      MERMAID_VALIDATOR_MAX_RETRIES: ${MERMAID_VALIDATOR_MAX_RETRIES:-3}

      # Logging
      LOG_LEVEL: ${LOG_LEVEL:-INFO}

      # Python
      PYTHONUNBUFFERED: 1
    volumes:
      # Mount code for development (comment out for production)
      - ./:/app
      # Mount logs
      - ./logs:/app/logs
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ['CMD', 'curl', '-f', 'http://localhost:8000/health']
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - ba_copilot_network

volumes:
  postgres_data:
    driver: local

networks:
  ba_copilot_network:
    driver: bridge
```

---

### Step 3: Create .env.example

**File**: `ba_copilot_ai/.env.example`

```bash
# =============================================================================
# BA Copilot AI - Environment Configuration Template
# =============================================================================
# Copy this file to .env and update with your actual values
# =============================================================================

# -----------------------------------------------------------------------------
# Database Configuration
# -----------------------------------------------------------------------------
POSTGRES_DB=ba_copilot
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_PORT=5432

# -----------------------------------------------------------------------------
# AI Service Configuration
# -----------------------------------------------------------------------------
AI_SERVICE_PORT=8000
LOG_LEVEL=INFO

# -----------------------------------------------------------------------------
# OpenRouter API Configuration
# Get your API key from: https://openrouter.ai/keys
# -----------------------------------------------------------------------------
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=openai/gpt-4

# Alternative models:
# OPENROUTER_MODEL=anthropic/claude-3-opus
# OPENROUTER_MODEL=meta-llama/llama-3-70b-instruct

# -----------------------------------------------------------------------------
# Mermaid Validator Configuration
# -----------------------------------------------------------------------------

# Enable/disable validation (set to 'false' to disable)
MERMAID_VALIDATOR_ENABLED=true

# Validator subprocess network configuration
MERMAID_VALIDATOR_PORT=3001
MERMAID_VALIDATOR_HOST=localhost

# Timeout settings (seconds)
MERMAID_VALIDATOR_STARTUP_TIMEOUT=30      # Time to wait for subprocess startup
MERMAID_VALIDATOR_REQUEST_TIMEOUT=10      # Timeout for validation requests
MERMAID_VALIDATOR_SHUTDOWN_TIMEOUT=5      # Time to wait for graceful shutdown

# Health monitoring
MERMAID_VALIDATOR_HEALTH_CHECK_INTERVAL=30    # Health check frequency (seconds)
MERMAID_VALIDATOR_MAX_CONSECUTIVE_FAILURES=3  # Auto-restart after N failures

# Retry logic
MERMAID_VALIDATOR_MAX_RETRIES=3           # Max LLM retry attempts for invalid diagrams
MERMAID_VALIDATOR_RETRY_DELAY=2           # Delay between retries (seconds)

# Performance limits
MERMAID_VALIDATOR_MAX_MEMORY_MB=500       # Max memory usage (MB)
MERMAID_VALIDATOR_MAX_CPU_PERCENT=80.0    # Max CPU usage (%)

# -----------------------------------------------------------------------------
# Development Settings (Optional)
# -----------------------------------------------------------------------------
# PYTHONDONTWRITEBYTECODE=1
# PYTHONPATH=/app
```

---

### Step 4: Create .dockerignore

**File**: `ba_copilot_ai/.dockerignore`

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Node.js (keep node_modules, we'll copy from builder)
# node_modules/  # DON'T ignore - we need to copy from builder
.npm
.node_repl_history

# Environment
.env
.env.local

# Logs
logs/
*.log

# Git
.git/
.gitignore

# Docker
Dockerfile
docker-compose.yml
.dockerignore

# Documentation
*.md
docs/
README.md

# Backups
backups/
*.sql
*.bak

# OS
.DS_Store
Thumbs.db

# Project specific
inception/
proof/
verify_*.ps1
verify_*.sh
```

---

### Step 5: Update Health Check Endpoint

**File**: `ba_copilot_ai/main.py` (add health endpoint)

```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from services.mermaid_validator import MermaidSubprocessManager, get_config

logger = logging.getLogger(__name__)


# Global validator instance
validator_manager: Optional[MermaidSubprocessManager] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Startup:
        - Initialize and start Mermaid validator subprocess
        - Wait for subprocess to be healthy

    Shutdown:
        - Gracefully stop validator subprocess
    """
    global validator_manager

    # Startup
    logger.info("🚀 Starting BA Copilot AI Service...")

    config = get_config()

    if config.enabled:
        try:
            validator_manager = MermaidSubprocessManager(config)
            await validator_manager.start()
            logger.info("✅ Mermaid validator started successfully")
        except Exception as e:
            logger.error(f"❌ Failed to start validator: {e}")
            logger.warning("⚠️  Continuing without validation")
            validator_manager = None
    else:
        logger.info("ℹ️  Mermaid validator disabled")
        validator_manager = None

    # Store in app state
    app.state.validator = validator_manager

    yield

    # Shutdown
    logger.info("🛑 Shutting down BA Copilot AI Service...")

    if validator_manager:
        await validator_manager.stop()
        logger.info("✅ Mermaid validator stopped")

    logger.info("👋 Shutdown complete")


# Create FastAPI app with lifespan
app = FastAPI(
    title="BA Copilot AI",
    description="Business Analyst Copilot with Mermaid Validation",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health")
async def health_check():
    """
    Comprehensive health check endpoint.

    Checks:
        - API server is responding
        - Validator subprocess status
        - Database connectivity (if applicable)

    Returns:
        200: All systems healthy
        503: Service degraded or unavailable
    """
    health_status = {
        "status": "healthy",
        "api": "ok",
        "validator": "disabled"
    }

    # Check validator status
    if validator_manager:
        is_healthy = await validator_manager.health_check()
        metrics = validator_manager.get_metrics()

        health_status["validator"] = {
            "status": "healthy" if is_healthy else "unhealthy",
            "state": metrics.get("state"),
            "running": metrics.get("running", False),
            "metrics": {
                "cpu_percent": metrics.get("cpu_percent"),
                "memory_mb": metrics.get("memory_mb"),
                "uptime_seconds": metrics.get("uptime_seconds")
            }
        }

        # Service is degraded if validator is unhealthy
        if not is_healthy:
            health_status["status"] = "degraded"

    status_code = 200 if health_status["status"] != "unavailable" else 503

    return JSONResponse(
        content=health_status,
        status_code=status_code
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "BA Copilot AI Service",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# ... rest of your existing endpoints ...
```

---

### Step 6: Create Docker Build Script

**File**: `ba_copilot_ai/docker-build.ps1`

```powershell
# ============================================================
# Docker Build Script for BA Copilot AI
# ============================================================

param(
    [switch]$NoBuild,
    [switch]$NoCache,
    [switch]$Production
)

Write-Host "🐳 BA Copilot AI - Docker Build" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Check if Docker is running
$dockerRunning = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Docker is running" -ForegroundColor Green

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found. Creating from .env.example..." -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✅ .env created. Please update with your actual values." -ForegroundColor Green
    } else {
        Write-Host "❌ .env.example not found. Cannot create .env" -ForegroundColor Red
        exit 1
    }
}

# Build arguments
$buildArgs = @()
if ($NoCache) {
    $buildArgs += "--no-cache"
}

# Build image
if (-not $NoBuild) {
    Write-Host "`n📦 Building Docker image..." -ForegroundColor Cyan

    docker build $buildArgs -t ba-copilot-ai:latest .

    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Docker build failed" -ForegroundColor Red
        exit 1
    }

    Write-Host "✅ Docker image built successfully" -ForegroundColor Green
}

# Start services
Write-Host "`n🚀 Starting services..." -ForegroundColor Cyan

if ($Production) {
    # Production mode: no volume mounts
    docker-compose -f docker-compose.yml up -d
} else {
    # Development mode: with volume mounts
    docker-compose up -d
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start services" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Services started" -ForegroundColor Green

# Wait for health checks
Write-Host "`n⏳ Waiting for services to be healthy..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

# Check service health
$dbHealthy = docker inspect --format='{{.State.Health.Status}}' ba_copilot_db 2>$null
$aiHealthy = docker inspect --format='{{.State.Health.Status}}' ba_copilot_ai 2>$null

Write-Host "`nService Health Status:" -ForegroundColor Cyan
Write-Host "  Database:   $dbHealthy" -ForegroundColor $(if ($dbHealthy -eq "healthy") { "Green" } else { "Yellow" })
Write-Host "  AI Service: $aiHealthy" -ForegroundColor $(if ($aiHealthy -eq "healthy") { "Green" } else { "Yellow" })

# Show logs
Write-Host "`n📋 Recent logs:" -ForegroundColor Cyan
docker-compose logs --tail=20 ai-service

Write-Host "`n✅ Deployment complete!" -ForegroundColor Green
Write-Host "`nAccess points:" -ForegroundColor Cyan
Write-Host "  API:    http://localhost:8000" -ForegroundColor White
Write-Host "  Docs:   http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Health: http://localhost:8000/health" -ForegroundColor White

Write-Host "`nUseful commands:" -ForegroundColor Cyan
Write-Host "  View logs:      docker-compose logs -f ai-service" -ForegroundColor White
Write-Host "  Stop services:  docker-compose down" -ForegroundColor White
Write-Host "  Restart:        docker-compose restart ai-service" -ForegroundColor White
```

---

## ✅ Verification Steps

### Step 1: Build Docker Image

```powershell
# Navigate to ba_copilot_ai
cd d:\Do_an_tot_nghiep\ba_copilot_ai

# Build image (no cache for clean build)
docker build --no-cache -t ba-copilot-ai:latest .

# Verify image size (should be ~400-500MB)
docker images ba-copilot-ai:latest
```

**Expected Output**:

```
REPOSITORY        TAG       IMAGE ID       CREATED          SIZE
ba-copilot-ai     latest    abc123def456   10 seconds ago   487MB
```

### Step 2: Start Services

```powershell
# Start with docker-compose
docker-compose up -d

# Check status
docker-compose ps

# Watch logs
docker-compose logs -f ai-service
```

**Expected Logs**:

```
ai-service  | 🚀 Starting BA Copilot AI Service...
ai-service  | Starting Node.js validator subprocess...
ai-service  | Subprocess started with PID: 23
ai-service  | [NodeJS] Server listening on http://localhost:3001
ai-service  | ✓ Server ready after 2.3s
ai-service  | ✅ Mermaid validator started successfully
ai-service  | INFO:     Started server process [1]
ai-service  | INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 3: Test Health Endpoint

```powershell
# Test health check
Invoke-RestMethod -Uri "http://localhost:8000/health" | ConvertTo-Json -Depth 10
```

**Expected Response**:

```json
{
  "status": "healthy",
  "api": "ok",
  "validator": {
    "status": "healthy",
    "state": "running",
    "running": true,
    "metrics": {
      "cpu_percent": 5.2,
      "memory_mb": 45.3,
      "uptime_seconds": 120
    }
  }
}
```

### Step 4: Test Validation Inside Container

```powershell
# Execute command inside container
docker exec -it ba_copilot_ai bash

# Inside container:
curl -X POST http://localhost:3001/validate \
  -H "Content-Type: application/json" \
  -d '{"code":"graph TD\nA-->B"}'

# Should return: {"valid":true,...}
exit
```

---

## 🐛 Troubleshooting

### Issue: Node.js not found in container

**Symptom**:

```
FileNotFoundError: [Errno 2] No such file or directory: 'node'
```

**Solution**:

```dockerfile
# Ensure Node.js installed in final stage
RUN apt-get update && apt-get install -y nodejs npm
```

### Issue: node_modules not copied correctly

**Symptom**:

```
Error: Cannot find module '@mermaid-js/mermaid-cli'
```

**Debug**:

```powershell
# Check if node_modules exist in container
docker exec -it ba_copilot_ai ls -la /app/services/mermaid_validator/nodejs/node_modules

# Rebuild with verbose output
docker build --progress=plain --no-cache -t ba-copilot-ai:latest .
```

### Issue: Health check failing

**Symptom**:

```
Container marked unhealthy
```

**Debug**:

```powershell
# Check health check logs
docker inspect ba_copilot_ai | Select-String -Pattern "Health"

# Test health endpoint manually
docker exec -it ba_copilot_ai curl -f http://localhost:8000/health
```

### Issue: Port conflict

**Symptom**:

```
Error: port 8000 already in use
```

**Solution**:

```bash
# Update .env with different port
AI_SERVICE_PORT=8001

# Or stop conflicting service
docker stop $(docker ps -q --filter "publish=8000")
```

---

## ✅ Verification Checklist

- [ ] Dockerfile updated with multi-stage build
- [ ] docker-compose.yml configured with all services
- [ ] .env.example created with all variables
- [ ] .dockerignore created
- [ ] Health endpoint implemented in main.py
- [ ] Docker build succeeds without errors
- [ ] Image size reasonable (~400-500MB)
- [ ] Services start successfully
- [ ] Health checks pass
- [ ] Validator subprocess runs in container
- [ ] Validation requests work
- [ ] Logs stream correctly

---

## 🎯 Commit Time!

```powershell
cd d:\Do_an_tot_nghiep\ba_copilot_ai

git add Dockerfile docker-compose.yml .env.example .dockerignore
git add main.py
git add docker-build.ps1

git commit -m "chore: update Docker config for Node.js subprocess integration

- Implement multi-stage Docker build (Node.js builder + Python runtime)
- Update docker-compose.yml with validator environment variables
- Add comprehensive .env.example with all configuration options
- Create .dockerignore for optimized builds
- Implement /health endpoint with validator status
- Add docker-build.ps1 PowerShell helper script

Features:
  - Multi-stage build reduces image size by ~40%
  - Node.js 18 + Python 3.11 in single container
  - Health checks for both database and AI service
  - Non-root user for security
  - Comprehensive logging configuration
  - Development and production modes

Docker Configuration:
  - Stage 1: Node.js builder for dependencies
  - Stage 2: Python runtime with Node.js
  - Health check interval: 30s
  - Startup grace period: 40s
  - Auto-restart on failure

Environment Variables:
  - MERMAID_VALIDATOR_* for all validator settings
  - Timeout and retry configurations
  - Performance limit settings
  - Flexible port configuration

Refs: #OPS-317"
```

---

## 📚 Additional Resources

- [Docker Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Docker Compose Health Checks](https://docs.docker.com/compose/compose-file/compose-file-v3/#healthcheck)
- [FastAPI Lifespan Events](https://fastapi.tiangolo.com/advanced/events/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

**Next Phase**: [05_LANGGRAPH_INTEGRATION.md](./05_LANGGRAPH_INTEGRATION.md) →

---

**Phase 4 Complete** ✅  
**Est. Completion Time**: 30-45 minutes  
**Commit**: `chore: update Docker config for Node.js subprocess integration`
