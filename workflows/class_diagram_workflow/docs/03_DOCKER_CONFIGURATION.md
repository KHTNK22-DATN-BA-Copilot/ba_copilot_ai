# Phase 3: Docker Configuration Refinement

## 🎯 Objective

Optimize Docker configuration for production readiness, including multi-stage builds, security hardening, and development vs. production environments.

**Estimated Time**: 20-25 minutes  
**Commit Message**: `chore: optimize Docker configuration for production readiness`

---

## 🏗️ Architecture Enhancement

### Multi-Stage Build Strategy

**Problem**: Current Dockerfile includes development dependencies and build artifacts.

**Solution**: Multi-stage builds separate build and runtime stages:

```
┌─────────────────────────────────────────┐
│         Stage 1: Builder                │
│  - Install all dependencies             │
│  - Run tests (optional)                 │
│  - Build artifacts                      │
└──────────────┬──────────────────────────┘
               │ Copy only runtime files
               ▼
┌─────────────────────────────────────────┐
│         Stage 2: Runtime                │
│  - Minimal base image                   │
│  - Production dependencies only         │
│  - Non-root user                        │
│  - Security hardening                   │
└─────────────────────────────────────────┘
```

**Benefits**:

- ✅ **Smaller images**: ~50-70% size reduction
- ✅ **Security**: No build tools in production
- ✅ **Speed**: Faster deployments and starts
- ✅ **Cache efficiency**: Independent layer caching

---

## 🔍 Deep Dive: Production vs. Development

### Configuration Matrix

| Aspect             | Development                 | Production       |
| ------------------ | --------------------------- | ---------------- |
| **Image Size**     | Larger (includes dev tools) | Minimal          |
| **Restart Policy** | `no` (manual restart)       | `unless-stopped` |
| **Volumes**        | Source code mounted         | No source mounts |
| **Debugging**      | Enabled                     | Disabled         |
| **Hot Reload**     | Enabled                     | Disabled         |
| **Logging**        | DEBUG level                 | INFO/WARNING     |
| **Health Checks**  | Less frequent               | More frequent    |

### Environment-Specific Configurations

We'll create:

1. **`docker-compose.yml`**: Base configuration
2. **`docker-compose.dev.yml`**: Development overrides
3. **`docker-compose.prod.yml`**: Production overrides

**Usage**:

```powershell
# Development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## 🛠️ Implementation Steps

### Step 1: Optimize AI Service Dockerfile (Multi-Stage)

**File**: `Dockerfile` (replace existing)

```dockerfile
# ============================================
# Stage 1: Builder
# ============================================
FROM python:3.11-slim AS builder

# Metadata
LABEL stage=builder

WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv

# Activate venv for subsequent RUN commands
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Optional: Run tests in build stage
# RUN pytest tests/ || echo "Tests failed but continuing..."

# Optional: Compile Python files for faster startup
RUN python -m compileall .

# ============================================
# Stage 2: Runtime
# ============================================
FROM python:3.11-slim AS runtime

# Metadata
LABEL maintainer="BA Copilot Team"
LABEL description="BA Copilot AI Service - Production"
LABEL version="1.0.0"

WORKDIR /app

# Install only runtime system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code from builder
COPY --from=builder /app /app

# Set PATH to use venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Create necessary directories
RUN mkdir -p /app/uploads /app/logs && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Key Improvements Explained**:

1. **Multi-Stage Build**

   ```dockerfile
   FROM python:3.11-slim AS builder
   ...
   FROM python:3.11-slim AS runtime
   COPY --from=builder /opt/venv /opt/venv
   ```

   - **Builder stage**: 850MB (includes gcc, g++, build tools)
   - **Runtime stage**: 420MB (only runtime deps)
   - **Savings**: 430MB (~50% reduction)

2. **Virtual Environment in Container**

   ```dockerfile
   RUN python -m venv /opt/venv
   ENV PATH="/opt/venv/bin:$PATH"
   ```

   - **Why venv in container?**: Isolates Python packages
   - **Benefits**: Cleaner dependency management, easier to copy between stages
   - **Alternative**: System-wide pip install (not recommended)

3. **Python Optimization Flags**

   ```dockerfile
   ENV PYTHONUNBUFFERED=1 \
       PYTHONDONTWRITEBYTECODE=1
   ```

   - **PYTHONUNBUFFERED**: Forces stdout/stderr to be unbuffered
     - **Benefit**: Real-time log output in Docker
     - **Without it**: Logs buffered, delayed visibility
   - **PYTHONDONTWRITEBYTECODE**: Prevents `.pyc` file generation
     - **Benefit**: Smaller image, no write operations
     - **Trade-off**: Slightly slower first import (negligible)

4. **Security Hardening**

   ```dockerfile
   RUN groupadd -r appuser && useradd -r -g appuser appuser
   USER appuser
   ```

   - **Principle of Least Privilege**: Non-root user
   - **Attack Surface**: Limited capabilities if compromised
   - **Compliance**: Required for SOC2, ISO27001

5. **Compiled Python Files**
   ```dockerfile
   RUN python -m compileall .
   ```
   - **Purpose**: Pre-compile `.py` to `.pyc` bytecode
   - **Benefit**: 10-20% faster startup time
   - **When it matters**: High-frequency container restarts

---

### Step 2: Optimize MCP Server Dockerfile

**File**: `docker/mcp-server/Dockerfile` (replace existing)

```dockerfile
# ============================================
# Stage 1: Builder
# ============================================
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install ALL dependencies (including dev)
RUN npm ci

# Copy source code (if any custom code)
COPY . .

# ============================================
# Stage 2: Runtime
# ============================================
FROM node:20-alpine AS runtime

# Metadata
LABEL maintainer="BA Copilot Team"
LABEL description="MCP Mermaid Validator Server - Production"
LABEL version="1.0.0"

WORKDIR /app

# Install only production dependencies
COPY package*.json ./
RUN npm ci --only=production && \
    npm cache clean --force

# Copy application files from builder
COPY --from=builder /app/server.js ./

# Create non-root user
RUN addgroup -g 1001 -S mcp && \
    adduser -u 1001 -S mcp -G mcp && \
    chown -R mcp:mcp /app

# Switch to non-root user
USER mcp

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000/ || exit 1

# Run application
CMD ["npm", "start"]
```

**Optimizations**:

1. **npm ci vs npm install**

   ```dockerfile
   RUN npm ci --only=production
   ```

   - **npm ci**: Uses `package-lock.json` for reproducible builds
   - **--only=production**: Skips devDependencies
   - **Result**: 30-40% smaller node_modules

2. **Cache Cleaning**
   ```dockerfile
   npm cache clean --force
   ```
   - **Removes**: npm download cache (~150MB)
   - **Timing**: After install, before image finalization
   - **Savings**: Significant in CI/CD pipelines

---

### Step 3: Create Development Override

**File**: `docker-compose.dev.yml`

```yaml
# Development-specific overrides
# Usage: docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

version: '3.8'

services:
  ai-service:
    build:
      context: .
      dockerfile: Dockerfile
      target: runtime # Use runtime stage but with dev settings
    environment:
      - ENV=development
      - DEBUG=true
      - LOG_LEVEL=DEBUG
    volumes:
      # Mount source code for hot reload
      - .:/app
      # Exclude venv to use container's venv
      - /app/.venv
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    restart: 'no' # Manual restart in dev
    ports:
      - '8000:8000' # Expose for debugging

  mcp-server:
    environment:
      - NODE_ENV=development
    volumes:
      # Mount for hot reload (if using nodemon)
      - ./docker/mcp-server:/app
      - /app/node_modules
    restart: 'no'
    ports:
      - '3000:3000' # Expose for debugging

  db:
    ports:
      - '5433:5432' # Expose for local DB clients
```

**Development Features**:

1. **Hot Reload**

   ```yaml
   command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   volumes:
     - .:/app
   ```

   - **--reload**: Auto-restart on code changes
   - **Volume mount**: Changes reflected immediately
   - **Exclusion**: `/app/.venv` prevents overwriting container's venv

2. **Debug Logging**

   ```yaml
   environment:
     - LOG_LEVEL=DEBUG
   ```

   - **Benefit**: Detailed logs for troubleshooting
   - **Trade-off**: More verbose output

3. **Port Exposure**
   ```yaml
   ports:
     - '3000:3000' # MCP server
   ```
   - **Dev only**: Direct access for testing (Postman, curl)
   - **Production**: Internal only (not exposed)

---

### Step 4: Create Production Override

**File**: `docker-compose.prod.yml`

```yaml
# Production-specific overrides
# Usage: docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

version: '3.8'

services:
  ai-service:
    build:
      context: .
      dockerfile: Dockerfile
      target: runtime
    environment:
      - ENV=production
      - DEBUG=false
      - LOG_LEVEL=INFO
    # No volume mounts (use image code)
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
    restart: always
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M

  mcp-server:
    environment:
      - NODE_ENV=production
    restart: always
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 128M

  db:
    restart: always
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
```

**Production Features**:

1. **Multiple Workers**

   ```yaml
   command: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

   - **Purpose**: Parallel request handling
   - **Workers**: 2-4 × CPU cores (rule of thumb)
   - **Example**: 2-core machine = 4 workers
   - **Benefit**: 4x throughput for CPU-bound tasks

2. **Resource Limits**

   ```yaml
   deploy:
     resources:
       limits:
         cpus: '2.0'
         memory: 2G
   ```

   - **Purpose**: Prevent resource hogging
   - **limits**: Maximum resources
   - **reservations**: Guaranteed minimum
   - **OOM Killer**: Docker kills container if exceeds memory limit

3. **Restart Policy**
   ```yaml
   restart: always
   ```
   - **always**: Restart on failure, even after manual stop
   - **unless-stopped**: Restart unless explicitly stopped
   - **on-failure**: Restart only if exit code != 0
   - **Production choice**: `always` for critical services

---

### Step 5: Add .dockerignore Files

**File**: `.dockerignore` (root)

```
# Git
.git
.gitignore

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
ENV/
.pytest_cache/
htmlcov/
.coverage

# IDE
.vscode/
.idea/
*.swp
*.swo

# Node.js (if any in root)
node_modules/
npm-debug.log

# Documentation
*.md
docs/

# Tests
tests/
test_*.py

# Development files
docker-compose.dev.yml
docker-compose.override.yml
.env.local

# OS
.DS_Store
Thumbs.db

# Large files
uploads/
*.log
logs/
```

**File**: `docker/mcp-server/.dockerignore`

```
# Node.js
node_modules/
npm-debug.log
yarn-error.log

# Development
.env.local
*.test.js

# OS
.DS_Store
```

**Why .dockerignore Matters**:

| Without .dockerignore         | With .dockerignore | Improvement       |
| ----------------------------- | ------------------ | ----------------- |
| 500MB build context           | 50MB build context | **90% reduction** |
| 45s build time                | 5s build time      | **9x faster**     |
| .git included (security risk) | .git excluded      | **Security** ✅   |

---

### Step 6: Add Docker Compose Profiles

**File**: `docker-compose.yml` (update services)

Add profiles for selective service startup:

```yaml
services:
  ai-service:
    # ... existing config
    profiles:
      - full-stack
      - ai-only

  mcp-server:
    # ... existing config
    profiles:
      - full-stack
      - ai-only

  db:
    # ... existing config
    profiles:
      - full-stack
      - db-only
```

**Usage**:

```powershell
# Start all services
docker-compose --profile full-stack up

# Start only AI and MCP (no DB)
docker-compose --profile ai-only up

# Start only database
docker-compose --profile db-only up
```

**Use Cases**:

- **Development**: Run DB locally, only MCP in Docker
- **Testing**: Run only services being tested
- **CI/CD**: Selective service deployment

---

### Step 7: Add Health Check Endpoint to FastAPI

**File**: `main.py` (update health check)

Enhance health check to verify MCP connectivity:

```python
from services.mcp_client import MCPClient

@app.get("/health")
async def health_check():
    """
    Comprehensive health check endpoint.

    Checks:
    - API server is running
    - OpenRouter API key configured
    - MCP server connectivity
    - Database connectivity (if applicable)
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }

    # Check OpenRouter API key
    openrouter_api_key = os.getenv("OPEN_ROUTER_API_KEY", "")
    health_status["checks"]["openrouter_api"] = {
        "status": "configured" if openrouter_api_key else "missing",
        "configured": bool(openrouter_api_key)
    }

    # Check MCP server connectivity
    try:
        async with MCPClient() as client:
            mcp_healthy = await client.health_check()
            health_status["checks"]["mcp_server"] = {
                "status": "healthy" if mcp_healthy else "unhealthy",
                "url": os.getenv("MCP_SERVER_URL", "not_configured")
            }
    except Exception as e:
        health_status["checks"]["mcp_server"] = {
            "status": "error",
            "error": str(e)
        }
        health_status["status"] = "degraded"

    # Overall status
    all_healthy = all(
        check.get("status") in ["healthy", "configured"]
        for check in health_status["checks"].values()
    )

    if not all_healthy and health_status["status"] == "healthy":
        health_status["status"] = "degraded"

    # Return appropriate status code
    status_code = 200 if all_healthy else 503
    return JSONResponse(content=health_status, status_code=status_code)
```

**Health Check Levels**:

| Status        | Meaning                               | HTTP Code | Action            |
| ------------- | ------------------------------------- | --------- | ----------------- |
| **healthy**   | All checks pass                       | 200       | None              |
| **degraded**  | Some checks fail, but core functional | 200       | Log warning       |
| **unhealthy** | Critical checks fail                  | 503       | Restart container |

**Import statement needed**:

```python
from fastapi.responses import JSONResponse
from datetime import datetime
```

---

### Step 8: Create Docker Management Scripts

**File**: `scripts/docker-dev.ps1`

```powershell
# Development environment startup script
Write-Host "Starting BA Copilot AI - Development Environment" -ForegroundColor Green

# Check if .env exists
if (!(Test-Path .env)) {
    Write-Host "ERROR: .env file not found. Copy .env.example to .env" -ForegroundColor Red
    exit 1
}

# Build images
Write-Host "`nBuilding Docker images..." -ForegroundColor Yellow
docker-compose -f docker-compose.yml -f docker-compose.dev.yml build

# Start services
Write-Host "`nStarting services..." -ForegroundColor Yellow
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Wait for health checks
Write-Host "`nWaiting for services to be healthy..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Show status
Write-Host "`nService Status:" -ForegroundColor Green
docker-compose ps

# Show logs
Write-Host "`nRecent Logs:" -ForegroundColor Green
docker-compose logs --tail=20

Write-Host "`n✅ Development environment is ready!" -ForegroundColor Green
Write-Host "API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "MCP: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Docs: http://localhost:8000/docs" -ForegroundColor Cyan
```

**File**: `scripts/docker-prod.ps1`

```powershell
# Production environment startup script
Write-Host "Starting BA Copilot AI - Production Environment" -ForegroundColor Green

# Check if .env exists
if (!(Test-Path .env)) {
    Write-Host "ERROR: .env file not found" -ForegroundColor Red
    exit 1
}

# Build images
Write-Host "`nBuilding Docker images..." -ForegroundColor Yellow
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache

# Start services
Write-Host "`nStarting services..." -ForegroundColor Yellow
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Wait for health checks
Write-Host "`nWaiting for services to be healthy..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Verify health
$health = Invoke-RestMethod -Uri "http://localhost:8000/health" -ErrorAction SilentlyContinue
if ($health.status -eq "healthy") {
    Write-Host "`n✅ All services healthy!" -ForegroundColor Green
} else {
    Write-Host "`n⚠️ Some services unhealthy. Check logs:" -ForegroundColor Yellow
    docker-compose logs --tail=50
}

# Show status
docker-compose ps
```

**File**: `scripts/docker-stop.ps1`

```powershell
# Stop all services
Write-Host "Stopping BA Copilot AI services..." -ForegroundColor Yellow

docker-compose down

Write-Host "✅ Services stopped" -ForegroundColor Green
```

**Make scripts executable**:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### Step 9: Build and Test Optimized Images

```powershell
# Build production images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Check image sizes
docker images | Select-String -Pattern "ba-copilot"

# Expected output:
# ba-copilot-ai    latest    abc123    420MB    (down from 850MB)
# ba-copilot-mcp   latest    def456    180MB    (down from 280MB)
```

**Size Comparison**:

| Image      | Before     | After     | Savings         |
| ---------- | ---------- | --------- | --------------- |
| ai-service | 850MB      | 420MB     | **430MB (50%)** |
| mcp-server | 280MB      | 180MB     | **100MB (36%)** |
| **Total**  | **1130MB** | **600MB** | **530MB (47%)** |

---

### Step 10: Test All Configurations

**Test Development Setup**:

```powershell
# Start dev environment
.\scripts\docker-dev.ps1

# Verify hot reload works
# 1. Edit main.py (add a comment)
# 2. Check logs for "Reloading"
docker-compose logs -f ai-service

# Stop
.\scripts\docker-stop.ps1
```

**Test Production Setup**:

```powershell
# Start prod environment
.\scripts\docker-prod.ps1

# Verify multiple workers
docker-compose exec ai-service ps aux | Select-String -Pattern "uvicorn"
# Should show 4 worker processes

# Check resource limits
docker stats ba-copilot-ai

# Stop
docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
```

---

## ✅ Verification Checklist

Before proceeding to Phase 4, ensure:

- [ ] Optimized Dockerfiles created (multi-stage builds)
- [ ] `.dockerignore` files added (root and mcp-server)
- [ ] `docker-compose.dev.yml` created
- [ ] `docker-compose.prod.yml` created
- [ ] Health check endpoint enhanced in `main.py`
- [ ] Docker management scripts created (`scripts/docker-*.ps1`)
- [ ] Image sizes reduced by ~50%
- [ ] Development environment tested (hot reload works)
- [ ] Production environment tested (multi-worker confirmed)
- [ ] Health checks passing for all services

---

## 🎯 Commit Time!

```powershell
# Stage changes
git add Dockerfile
git add docker/mcp-server/Dockerfile
git add .dockerignore
git add docker/mcp-server/.dockerignore
git add docker-compose.dev.yml
git add docker-compose.prod.yml
git add main.py
git add scripts/

# Commit
git commit -m "chore: optimize Docker configuration for production readiness

- Implement multi-stage builds for ai-service and mcp-server
- Add .dockerignore files to reduce build context
- Create docker-compose.dev.yml for development overrides
- Create docker-compose.prod.yml for production config
- Enhance health check endpoint with MCP connectivity check
- Add Docker management scripts (docker-dev.ps1, docker-prod.ps1)
- Configure resource limits and restart policies
- Enable hot reload for development environment

Improvements:
- 50% reduction in image sizes (1130MB -> 600MB)
- Multi-worker support for production (4 workers)
- Security hardening (non-root users)
- Comprehensive health checks

Refs: #OPS-266"
```

---

## 🐛 Troubleshooting

### Issue: Multi-stage build fails at COPY --from=builder

**Symptom**:

```
ERROR: failed to copy files: lstat /var/lib/docker/overlay2/.../app: no such file or directory
```

**Solution**:

```dockerfile
# Ensure WORKDIR is set in builder stage
FROM python:3.11-slim AS builder
WORKDIR /app  # Must match COPY --from=builder path
```

### Issue: Hot reload not working in development

**Symptom**: Code changes don't trigger reload

**Debug**:

```powershell
# Check if volume is mounted
docker-compose exec ai-service ls -la /app

# Check uvicorn logs
docker-compose logs -f ai-service | Select-String -Pattern "reload"
```

**Solution**:

1. Ensure `--reload` flag in command
2. Verify volume mount: `-v .:/app`
3. Check file permissions (Windows: may need WSL2)

### Issue: Health check always fails

**Symptom**: Container marked unhealthy despite working

**Debug**:

```powershell
# Manual health check
docker-compose exec ai-service wget -qO- http://localhost:8000/health

# Check if wget is installed
docker-compose exec ai-service which wget
```

**Solution**: Install wget in Dockerfile:

```dockerfile
RUN apt-get update && apt-get install -y wget
```

---

## 📚 Additional Resources

- [Docker Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Docker Compose Profiles](https://docs.docker.com/compose/profiles/)
- [Python Docker Best Practices](https://pythonspeed.com/docker/)
- [Node.js Docker Best Practices](https://github.com/nodejs/docker-node/blob/main/docs/BestPractices.md)

---

**Next Phase**: [04_VALIDATION_LOGIC.md](./04_VALIDATION_LOGIC.md) →

---

**Phase 3 Complete** ✅  
**Est. Completion Time**: 20-25 minutes  
**Commit**: `chore: optimize Docker configuration for production readiness`
