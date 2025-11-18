# Phase 7: Deployment Verification

## 🎯 Objective

Verify complete implementation, run all tests, build and deploy Docker containers, validate production readiness, and document deployment procedures.

**Estimated Time**: 30-45 minutes  
**Commit Message**: `chore: verify full stack with validation enabled`

---

## 🚀 Deployment Checklist

### Pre-Deployment Verification

```
┌───────────────────────────────────────────┐
│         Pre-Deployment Checks             │
├───────────────────────────────────────────┤
│ ✓ All dependencies installed              │
│ ✓ Node.js validator service created       │
│ ✓ Python subprocess manager implemented   │
│ ✓ Docker configuration updated            │
│ ✓ Workflows integrated with validation    │
│ ✓ Comprehensive tests written and passing │
│ ✓ Environment variables configured        │
│ ✓ Documentation complete                  │
└───────────────────────────────────────────┘
```

---

## 🛠️ Verification Steps

### Step 1: Verify Local Dependencies

**Create Verification Script**: `verify_full_setup.ps1`

```powershell
# ============================================================
# Full Stack Verification Script
# ============================================================

Write-Host "🔍 BA Copilot AI - Full Stack Verification" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan

$errors = @()

# ============================================================
# 1. Python Environment
# ============================================================
Write-Host "`n[1/8] Checking Python environment..." -ForegroundColor Yellow

try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ Python: $pythonVersion" -ForegroundColor Green
} catch {
    $errors += "Python not found"
    Write-Host "  ✗ Python not found" -ForegroundColor Red
}

# Check venv
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "  ✓ Virtual environment exists" -ForegroundColor Green
} else {
    $errors += "Virtual environment not found"
    Write-Host "  ✗ Virtual environment not found" -ForegroundColor Red
}

# ============================================================
# 2. Python Dependencies
# ============================================================
Write-Host "`n[2/8] Checking Python dependencies..." -ForegroundColor Yellow

$requiredPackages = @("httpx", "psutil", "pytest-asyncio", "pytest-mock", "pytest-timeout", "pytest-cov")

foreach ($package in $requiredPackages) {
    try {
        $result = python -c "import $package; print($package.__version__)" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ $package installed: $result" -ForegroundColor Green
        } else {
            $errors += "$package not installed"
            Write-Host "  ✗ $package not installed" -ForegroundColor Red
        }
    } catch {
        $errors += "$package not installed"
        Write-Host "  ✗ $package not installed" -ForegroundColor Red
    }
}

# ============================================================
# 3. Node.js Environment
# ============================================================
Write-Host "`n[3/8] Checking Node.js environment..." -ForegroundColor Yellow

try {
    $nodeVersion = node --version
    Write-Host "  ✓ Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    $errors += "Node.js not found"
    Write-Host "  ✗ Node.js not found" -ForegroundColor Red
}

try {
    $npmVersion = npm --version
    Write-Host "  ✓ npm: $npmVersion" -ForegroundColor Green
} catch {
    $errors += "npm not found"
    Write-Host "  ✗ npm not found" -ForegroundColor Red
}

# ============================================================
# 4. Node.js Dependencies
# ============================================================
Write-Host "`n[4/8] Checking Node.js dependencies..." -ForegroundColor Yellow

$nodejsPath = "services\mermaid_validator\nodejs"

if (Test-Path "$nodejsPath\package.json") {
    Write-Host "  ✓ package.json exists" -ForegroundColor Green

    if (Test-Path "$nodejsPath\node_modules") {
        Write-Host "  ✓ node_modules exists" -ForegroundColor Green

        # Check critical packages
        $criticalPackages = @("express", "@mermaid-js/mermaid-cli")
        foreach ($pkg in $criticalPackages) {
            if (Test-Path "$nodejsPath\node_modules\$pkg") {
                Write-Host "  ✓ $pkg installed" -ForegroundColor Green
            } else {
                $errors += "$pkg not installed"
                Write-Host "  ✗ $pkg not installed" -ForegroundColor Red
            }
        }
    } else {
        $errors += "node_modules not found"
        Write-Host "  ✗ node_modules not found (run npm install)" -ForegroundColor Red
    }
} else {
    $errors += "package.json not found"
    Write-Host "  ✗ package.json not found" -ForegroundColor Red
}

# ============================================================
# 5. Project Structure
# ============================================================
Write-Host "`n[5/8] Checking project structure..." -ForegroundColor Yellow

$requiredFiles = @(
    "services\mermaid_validator\config.py",
    "services\mermaid_validator\subprocess_manager.py",
    "services\mermaid_validator\client.py",
    "services\mermaid_validator\exceptions.py",
    "services\mermaid_validator\nodejs\server.js",
    "services\mermaid_validator\nodejs\validator.js",
    "Dockerfile",
    "docker-compose.yml",
    ".env.example"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        $errors += "$file missing"
        Write-Host "  ✗ $file missing" -ForegroundColor Red
    }
}

# ============================================================
# 6. Environment Configuration
# ============================================================
Write-Host "`n[6/8] Checking environment configuration..." -ForegroundColor Yellow

if (Test-Path ".env") {
    Write-Host "  ✓ .env file exists" -ForegroundColor Green

    # Check critical variables
    $envContent = Get-Content ".env" -Raw
    $criticalVars = @("OPENROUTER_API_KEY", "MERMAID_VALIDATOR_ENABLED")

    foreach ($var in $criticalVars) {
        if ($envContent -match $var) {
            Write-Host "  ✓ $var configured" -ForegroundColor Green
        } else {
            Write-Host "  ⚠ $var not found in .env" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "  ⚠ .env file not found (using defaults)" -ForegroundColor Yellow
}

# ============================================================
# 7. Docker
# ============================================================
Write-Host "`n[7/8] Checking Docker..." -ForegroundColor Yellow

try {
    $dockerVersion = docker --version
    Write-Host "  ✓ Docker: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ Docker not found (optional)" -ForegroundColor Yellow
}

try {
    docker-compose --version | Out-Null
    Write-Host "  ✓ Docker Compose available" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ Docker Compose not found (optional)" -ForegroundColor Yellow
}

# ============================================================
# 8. Test Suite
# ============================================================
Write-Host "`n[8/8] Checking test suite..." -ForegroundColor Yellow

$testFiles = Get-ChildItem -Path "tests" -Filter "test_*.py" -Recurse

if ($testFiles.Count -gt 0) {
    Write-Host "  ✓ Found $($testFiles.Count) test files" -ForegroundColor Green
} else {
    $errors += "No test files found"
    Write-Host "  ✗ No test files found" -ForegroundColor Red
}

# ============================================================
# Summary
# ============================================================
Write-Host "`n=============================================" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

if ($errors.Count -eq 0) {
    Write-Host "`n✅ All checks passed! Ready for deployment." -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n❌ Found $($errors.Count) issue(s):" -ForegroundColor Red
    foreach ($error in $errors) {
        Write-Host "  - $error" -ForegroundColor Red
    }
    Write-Host "`nPlease fix these issues before deployment." -ForegroundColor Yellow
    exit 1
}
```

---

### Step 2: Run Full Test Suite

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run all tests with coverage
pytest --cov=services.mermaid_validator --cov=workflows --cov-report=html --cov-report=term

# Check coverage
Start-Process .\htmlcov\index.html
```

**Expected Output**:

```
====================== test session starts ======================
collected 45 items

tests/unit/test_config.py ..................      [ 40%]
tests/unit/test_exceptions.py ....                [ 48%]
tests/integration/test_subprocess.py .....        [ 60%]
tests/integration/test_client.py .....            [ 72%]
tests/integration/test_workflow.py .....          [ 84%]
tests/e2e/test_full_stack.py ..                   [ 88%]
tests/performance/test_performance.py ...         [100%]

---------- coverage: platform win32, python 3.11 -----------
Name                                        Stmts   Miss  Cover
---------------------------------------------------------------
services/mermaid_validator/__init__.py         10      0   100%
services/mermaid_validator/config.py           45      2    96%
services/mermaid_validator/client.py           78      5    94%
services/mermaid_validator/exceptions.py       12      0   100%
services/mermaid_validator/subprocess.py      150     10    93%
workflows/class_diagram_workflow/*            120      8    93%
---------------------------------------------------------------
TOTAL                                         415     25    94%

==================== 45 passed in 45.23s ====================
```

---

### Step 3: Test Node.js Validator Standalone

```powershell
# Navigate to nodejs directory
cd services\mermaid_validator\nodejs

# Run validator server
node server.js
```

**In another terminal**:

```powershell
# Test validation endpoint
Invoke-RestMethod -Method POST -Uri "http://localhost:3001/validate" `
  -ContentType "application/json" `
  -Body '{"code":"classDiagram\n  class User"}' | ConvertTo-Json -Depth 10

# Test health endpoint
Invoke-RestMethod -Uri "http://localhost:3001/health" | ConvertTo-Json
```

**Expected Output**:

```json
{
  "valid": true,
  "code": "classDiagram\n  class User",
  "diagram_type": "classDiagram",
  "timestamp": 1699999999,
  "duration_ms": 125
}
```

---

### Step 4: Build Docker Image

```powershell
# Navigate to ba_copilot_ai root
cd d:\Do_an_tot_nghiep\ba_copilot_ai

# Build with no cache for clean build
docker build --no-cache -t ba-copilot-ai:latest .

# Verify image
docker images ba-copilot-ai
```

**Expected Output**:

```
REPOSITORY        TAG       IMAGE ID       CREATED          SIZE
ba-copilot-ai     latest    abc123def456   30 seconds ago   487MB
```

**Verify image layers**:

```powershell
docker history ba-copilot-ai:latest
```

---

### Step 5: Deploy with Docker Compose

```powershell
# Ensure .env exists
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "⚠️  Update .env with your API keys!" -ForegroundColor Yellow
    exit 1
}

# Start services
docker-compose up -d

# Check status
docker-compose ps

# Watch logs
docker-compose logs -f ai-service
```

**Expected Logs**:

```
ai-service  | INFO:     Started server process [1]
ai-service  | 🚀 Starting BA Copilot AI Service...
ai-service  | Starting Node.js validator subprocess...
ai-service  | Subprocess started with PID: 23
ai-service  | [NodeJS] Server listening on http://localhost:3001
ai-service  | ✓ Server ready after 2.1s
ai-service  | ✅ Mermaid validator started successfully
ai-service  | INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

### Step 6: Verify Running Services

```powershell
# Check health
Invoke-RestMethod -Uri "http://localhost:8000/health" | ConvertTo-Json -Depth 10

# Test diagram generation
$body = @{
    description = "Create a User class with name, email, and login method"
} | ConvertTo-Json

Invoke-RestMethod -Method POST -Uri "http://localhost:8000/generate/class-diagram" `
  -ContentType "application/json" `
  -Body $body | ConvertTo-Json -Depth 10
```

**Expected Health Response**:

```json
{
  "status": "healthy",
  "api": "ok",
  "validator": {
    "status": "healthy",
    "state": "running",
    "running": true,
    "metrics": {
      "cpu_percent": 3.2,
      "memory_mb": 42.5,
      "uptime_seconds": 120
    }
  }
}
```

**Expected Diagram Response**:

```json
{
  "type": "class_diagram",
  "detail": "classDiagram\n  class User {\n    +String name\n    +String email\n    +login()\n  }",
  "metadata": {
    "validated": true,
    "retry_count": 0,
    "validation_status": "valid",
    "validation": {
      "diagram_type": "classDiagram",
      "duration_ms": 145
    }
  }
}
```

---

### Step 7: Performance Benchmarking

**Create Benchmark Script**: `benchmark_validation.ps1`

```powershell
# ============================================================
# Validation Performance Benchmark
# ============================================================

Write-Host "⚡ Validation Performance Benchmark" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan

$endpoint = "http://localhost:8000/generate/class-diagram"
$iterations = 10

$latencies = @()

Write-Host "`nRunning $iterations requests..." -ForegroundColor Yellow

for ($i = 1; $i -le $iterations; $i++) {
    $body = @{
        description = "Create a simple User class with name attribute"
    } | ConvertTo-Json

    $start = Get-Date

    try {
        $response = Invoke-RestMethod -Method POST -Uri $endpoint `
          -ContentType "application/json" `
          -Body $body

        $end = Get-Date
        $latency = ($end - $start).TotalMilliseconds
        $latencies += $latency

        $validated = $response.metadata.validated
        $retries = $response.metadata.retry_count

        Write-Host "  Request $i : $([math]::Round($latency, 0))ms (validated=$validated, retries=$retries)" -ForegroundColor Green
    } catch {
        Write-Host "  Request $i : FAILED" -ForegroundColor Red
    }
}

# Calculate statistics
$avg = ($latencies | Measure-Object -Average).Average
$min = ($latencies | Measure-Object -Minimum).Minimum
$max = ($latencies | Measure-Object -Maximum).Maximum

Write-Host "`n📊 Statistics:" -ForegroundColor Cyan
Write-Host "  Average: $([math]::Round($avg, 0))ms" -ForegroundColor White
Write-Host "  Min:     $([math]::Round($min, 0))ms" -ForegroundColor White
Write-Host "  Max:     $([math]::Round($max, 0))ms" -ForegroundColor White

# Check against targets
if ($avg -lt 3000) {
    Write-Host "`n✅ Performance target met (< 3s average)" -ForegroundColor Green
} else {
    Write-Host "`n⚠️  Performance target missed (> 3s average)" -ForegroundColor Yellow
}
```

---

### Step 8: Create Deployment Checklist

**File**: `DEPLOYMENT_CHECKLIST.md`

````markdown
# BA Copilot AI - Deployment Checklist

## Pre-Deployment

- [ ] All dependencies installed (Python & Node.js)
- [ ] Virtual environment activated
- [ ] `.env` file configured with API keys
- [ ] All tests passing (90%+ coverage)
- [ ] Code committed to version control
- [ ] Documentation complete

## Local Testing

- [ ] Node.js validator runs standalone
- [ ] Python subprocess manager works
- [ ] Workflows integrate validation
- [ ] Health checks pass
- [ ] Performance benchmarks meet targets

## Docker Deployment

- [ ] Docker image builds successfully
- [ ] Image size reasonable (~400-500MB)
- [ ] Multi-stage build optimized
- [ ] docker-compose.yml configured
- [ ] Environment variables set
- [ ] Services start without errors
- [ ] Health checks pass in container
- [ ] Validation works in container

## Production Readiness

- [ ] All error handling tested
- [ ] Graceful degradation works
- [ ] Retry logic functions correctly
- [ ] Logging configured properly
- [ ] Monitoring in place
- [ ] Backup procedures documented
- [ ] Rollback plan prepared

## Post-Deployment

- [ ] Services running and healthy
- [ ] Validation latency < 500ms
- [ ] Subprocess auto-restart works
- [ ] No memory leaks (monitor 24h)
- [ ] Error logs reviewed
- [ ] Performance metrics logged
- [ ] User acceptance testing

## Rollback Procedure

If issues arise:

1. Stop services: `docker-compose down`
2. Revert to previous version
3. Rebuild: `docker build -t ba-copilot-ai:rollback .`
4. Restart: `docker-compose up -d`
5. Verify health: `curl http://localhost:8000/health`

## Monitoring Commands

```powershell
# Service status
docker-compose ps

# Logs (all services)
docker-compose logs -f

# Logs (ai-service only)
docker-compose logs -f ai-service

# Resource usage
docker stats

# Health check
Invoke-RestMethod http://localhost:8000/health

# Subprocess metrics
Invoke-RestMethod http://localhost:8000/health |
  Select-Object -ExpandProperty validator |
  ConvertTo-Json -Depth 10
```
````

## Support Contacts

- **Development Team**: [team@example.com](mailto:team@example.com)
- **DevOps**: [devops@example.com](mailto:devops@example.com)
- **On-Call**: +1-555-0100

---

**Last Updated**: November 18, 2025  
**Version**: 1.0.0

````

---

## ✅ Final Verification Checklist

### Code Quality
- [ ] All code follows PEP 8 (Python)
- [ ] All code follows ESLint (Node.js)
- [ ] Type hints present
- [ ] Documentation strings complete
- [ ] No TODO comments remaining

### Testing
- [ ] All tests pass
- [ ] Coverage > 90%
- [ ] Performance tests meet targets
- [ ] Integration tests pass
- [ ] E2E tests pass

### Docker
- [ ] Image builds successfully
- [ ] Image size optimized
- [ ] Services start correctly
- [ ] Health checks pass
- [ ] Validation works in container

### Documentation
- [ ] README.md updated
- [ ] API documentation complete
- [ ] Deployment guide written
- [ ] Troubleshooting documented
- [ ] Architecture documented

### Production Ready
- [ ] Error handling comprehensive
- [ ] Logging configured
- [ ] Monitoring enabled
- [ ] Security reviewed
- [ ] Performance optimized

---

## 🎯 Final Commit!

```powershell
cd d:\Do_an_tot_nghiep\ba_copilot_ai

# Stage all final changes
git add .

# Final commit
git commit -m "chore: verify full stack with validation enabled

- Create full stack verification script
- Add Docker deployment procedures
- Implement performance benchmarking
- Create deployment checklist
- Verify all components working together

Verification:
  - All dependencies installed and verified
  - Test suite passing with 94% coverage
  - Docker image builds successfully (~487MB)
  - Services deploy and run correctly
  - Validation works in all environments
  - Performance meets targets (< 500ms validation)

Deployment:
  - Docker multi-stage build optimized
  - docker-compose orchestration tested
  - Health checks passing
  - Subprocess management verified
  - Graceful degradation confirmed

Production Readiness:
  ✅ All tests passing
  ✅ Coverage > 90%
  ✅ Docker deployment verified
  ✅ Performance benchmarks met
  ✅ Documentation complete
  ✅ Monitoring in place

Scripts Added:
  - verify_full_setup.ps1: Pre-deployment verification
  - benchmark_validation.ps1: Performance testing
  - DEPLOYMENT_CHECKLIST.md: Deployment guide

Refs: #OPS-317"

# Tag release
git tag -a v1.0.0 -m "Release: Mermaid Validation System"

# Push to remote
git push origin OPS-317-mermaid-validation
git push origin v1.0.0
````

---

## 🎉 Deployment Complete!

### What You've Built

✅ **Node.js Validation Service**: Express server with @mermaid-js/mermaid-cli  
✅ **Python Subprocess Manager**: Lifecycle management with auto-recovery  
✅ **LangGraph Integration**: Validation + retry nodes in workflows  
✅ **Docker Deployment**: Multi-stage build with both runtimes  
✅ **Comprehensive Tests**: 90%+ coverage, unit/integration/e2e  
✅ **Production Ready**: Monitoring, logging, error handling

### Performance Metrics

- **Validation Latency**: ~150ms average
- **Subprocess Startup**: ~2s
- **End-to-End Request**: < 3s
- **Memory Usage**: ~50MB subprocess
- **Test Coverage**: 94%

### Next Steps

1. **Monitor Production**: Watch logs for first 24 hours
2. **Collect Metrics**: Track validation success rate
3. **User Feedback**: Gather feedback on diagram quality
4. **Iterate**: Improve prompts based on validation errors
5. **Scale**: Consider multiple validator instances if needed

---

## 📚 Documentation Reference

- [Phase 0: Implementation Overview](./00_IMPLEMENTATION_OVERVIEW.md)
- [Phase 1: Dependencies Setup](./01_DEPENDENCIES_SETUP.md)
- [Phase 2: Node.js Validator](./02_NODEJS_VALIDATOR_SERVICE.md)
- [Phase 3: Subprocess Manager](./03_PYTHON_SUBPROCESS_MANAGER.md)
- [Phase 4: Docker Configuration](./04_DOCKER_CONFIGURATION.md)
- [Phase 5: LangGraph Integration](./05_LANGGRAPH_INTEGRATION.md)
- [Phase 6: Comprehensive Testing](./06_COMPREHENSIVE_TESTING.md)
- [Phase 7: Deployment Verification](./07_DEPLOYMENT_VERIFICATION.md) (You are here)

---

**🎊 Congratulations! Your Mermaid validation system is live!**

---

**Phase 7 Complete** ✅  
**Est. Completion Time**: 30-45 minutes  
**Commit**: `chore: verify full stack with validation enabled`  
**Total Implementation Time**: ~6.5 hours

---

**Last Updated**: November 18, 2025  
**Version**: 1.0.0  
**Status**: Production Ready 🚀
