# Phase 2: MCP Server Setup

## 🎯 Objective

Configure and integrate the MCP Mermaid Validator server as a persistent service that runs alongside the FastAPI application.

**Estimated Time**: 25-30 minutes  
**Commit Message**: `feat: configure MCP server with Docker integration`

---

## 🏗️ Architecture Deep Dive

### Process Management Strategy

We'll implement a **multi-process architecture** where MCP server runs as an independent service:

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Host                          │
│                                                         │
│  ┌──────────────────┐         ┌──────────────────┐    │
│  │  ai-service      │         │  mcp-server      │    │
│  │  (Python/FastAPI)│◄───────►│  (Node.js)       │    │
│  │  Port: 8000      │  HTTP   │  Port: 3000      │    │
│  └──────────────────┘         └──────────────────┘    │
│                                                         │
│           Docker Network: ba-network                    │
└─────────────────────────────────────────────────────────┘
```

**Alternative Architectures Considered**:

| Architecture                   | Pros                                 | Cons                              | Decision    |
| ------------------------------ | ------------------------------------ | --------------------------------- | ----------- |
| **Separate Container** ✅      | Independent scaling, fault isolation | More containers                   | **CHOSEN**  |
| Single container w/ supervisor | Simpler deployment                   | Violates single-process principle | ❌ Rejected |
| Embedded subprocess            | Easy setup                           | Tight coupling, harder debugging  | ❌ Rejected |
| External managed service       | Best isolation                       | Complex infrastructure            | ❌ Overkill |

**Why Separate Container Wins**:

1. **Docker Philosophy**: One process per container
2. **Fault Isolation**: MCP crash doesn't affect FastAPI
3. **Independent Scaling**: Can scale MCP server independently
4. **Health Monitoring**: Separate health checks per service
5. **Language Isolation**: Node.js and Python environments separated

---

## 📁 File Structure

We'll create these files:

```
ba_copilot_ai/
├── docker/
│   └── mcp-server/
│       ├── Dockerfile          # MCP server image
│       ├── package.json        # Node.js dependencies
│       └── server.js           # Wrapper script (optional)
├── docker-compose.yml          # Updated with MCP service
├── .env                        # Environment variables
└── services/
    └── mcp_client.py           # Already created in Phase 1
```

---

## 🔍 Deep Dive: MCP Server Configuration

### Understanding the MCP Server

**What it does**:

- Listens on HTTP port (default 3000)
- Accepts JSON-RPC 2.0 requests
- Validates Mermaid syntax using `mermaid.js` parser
- Returns structured validation results

**JSON-RPC 2.0 Protocol**:

**Request Format**:

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "validate_mermaid",
    "arguments": {
      "code": "graph TD\n  A-->B"
    }
  },
  "id": 1
}
```

**Success Response**:

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

**Error Response**:

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32602,
    "message": "Invalid parameters",
    "data": {
      "errors": ["Syntax error at line 2"]
    }
  },
  "id": 1
}
```

---

## 🛠️ Implementation Steps

### Step 1: Create MCP Server Docker Directory

```powershell
# Create directory structure
New-Item -ItemType Directory -Path "docker\mcp-server" -Force

# Verify
Get-ChildItem -Path "docker\mcp-server"
```

---

### Step 2: Create MCP Server Dockerfile

**File**: `docker/mcp-server/Dockerfile`

```dockerfile
# MCP Mermaid Validator Server
# Base: Node.js 20 Alpine (lightweight)
FROM node:20-alpine

# Metadata
LABEL maintainer="BA Copilot Team"
LABEL description="MCP Mermaid Validator Server"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install global package manager
RUN npm install -g npm@latest

# Install MCP Mermaid Validator
# Using global install for simplicity
RUN npm install -g @rtuin/mcp-mermaid-validator

# Create non-root user for security
RUN addgroup -g 1001 -S mcp && \
    adduser -u 1001 -S mcp -G mcp

# Switch to non-root user
USER mcp

# Expose port 3000
EXPOSE 3000

# Health check
# Verify server responds to HTTP requests
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000/health || exit 1

# Run MCP server
# Note: Adjust command based on how @rtuin/mcp-mermaid-validator exposes binary
CMD ["npx", "@rtuin/mcp-mermaid-validator"]

# Alternative if package provides direct binary:
# CMD ["mcp-mermaid-validator"]
```

**Key Design Decisions**:

1. **Base Image: node:20-alpine**

   - **Why Alpine?**: 40MB vs 900MB for standard Node image
   - **Trade-off**: Some native modules may need build tools
   - **Decision**: MCP validator is pure JS, Alpine is safe

2. **Global npm Install**

   ```dockerfile
   RUN npm install -g @rtuin/mcp-mermaid-validator
   ```

   - **Why Global?**: Simplifies PATH management
   - **Alternative**: Local install with `package.json`
   - **Decision**: Global install for single-purpose container

3. **Non-root User**

   ```dockerfile
   USER mcp
   ```

   - **Security Best Practice**: Never run as root in container
   - **Principle of Least Privilege**: Limit container capabilities
   - **Compliance**: Required for many security audits

4. **Health Check Strategy**
   ```dockerfile
   HEALTHCHECK --interval=30s ...
   ```
   - **Purpose**: Docker monitors container health
   - **Action**: Auto-restart if unhealthy
   - **Endpoint**: Assumes `/health` endpoint (may need adjustment)

**Troubleshooting Note**: If MCP validator doesn't expose `/health`, we'll modify health check to:

```dockerfile
HEALTHCHECK CMD node -e "require('http').get('http://localhost:3000', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"
```

---

### Step 3: Create package.json (Optional but Recommended)

**File**: `docker/mcp-server/package.json`

```json
{
  "name": "ba-copilot-mcp-server",
  "version": "1.0.0",
  "description": "MCP Mermaid Validator Server for BA Copilot",
  "private": true,
  "scripts": {
    "start": "npx @rtuin/mcp-mermaid-validator",
    "dev": "nodemon --exec npx @rtuin/mcp-mermaid-validator",
    "test": "echo 'No tests defined'"
  },
  "dependencies": {
    "@rtuin/mcp-mermaid-validator": "^1.0.0"
  },
  "engines": {
    "node": ">=18.0.0",
    "npm": ">=9.0.0"
  },
  "keywords": ["mcp", "mermaid", "validation", "ba-copilot"],
  "author": "BA Copilot Team",
  "license": "MIT"
}
```

**Why package.json?**

- **Dependency Locking**: Ensures reproducible builds
- **Version Control**: Track exact package versions
- **Scripts**: Standardize start commands
- **Documentation**: Clear dependency declaration

**Update Dockerfile to use package.json**:

```dockerfile
# ... (previous content)

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# ... (rest of Dockerfile)

CMD ["npm", "start"]
```

**npm ci vs npm install**:
| Command | Use Case | Speed | Reproducibility |
|---------|----------|-------|-----------------|
| `npm install` | Development | Moderate | Medium |
| `npm ci` | CI/CD, Production | Faster | **High** ✅ |

**Decision**: Use `npm ci` for production builds.

---

### Step 4: Create Server Wrapper (Advanced, Optional)

For better control and monitoring, create a wrapper script:

**File**: `docker/mcp-server/server.js`

```javascript
/**
 * MCP Server Wrapper
 *
 * Provides:
 * - Custom health check endpoint
 * - Graceful shutdown handling
 * - Request logging
 * - Error monitoring
 */

const { spawn } = require('child_process');
const http = require('http');

// Configuration
const MCP_PORT = process.env.MCP_PORT || 3000;
const HEALTH_PORT = process.env.HEALTH_PORT || 3001;

// Health check server
const healthServer = http.createServer((req, res) => {
  if (req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(
      JSON.stringify({
        status: 'healthy',
        uptime: process.uptime(),
        timestamp: new Date().toISOString(),
      })
    );
  } else {
    res.writeHead(404);
    res.end();
  }
});

healthServer.listen(HEALTH_PORT, () => {
  console.log(`Health check server running on port ${HEALTH_PORT}`);
});

// Start MCP validator
const mcpProcess = spawn('npx', ['@rtuin/mcp-mermaid-validator'], {
  stdio: 'inherit',
  env: { ...process.env, PORT: MCP_PORT },
});

mcpProcess.on('error', (err) => {
  console.error('Failed to start MCP server:', err);
  process.exit(1);
});

mcpProcess.on('exit', (code) => {
  console.error(`MCP server exited with code ${code}`);
  process.exit(code);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully...');
  mcpProcess.kill('SIGTERM');
  healthServer.close(() => {
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  console.log('SIGINT received, shutting down gracefully...');
  mcpProcess.kill('SIGINT');
  healthServer.close(() => {
    process.exit(0);
  });
});

console.log(`Starting MCP Mermaid Validator on port ${MCP_PORT}`);
```

**Benefits of Wrapper**:

- ✅ Separate health check endpoint (port 3001)
- ✅ Graceful shutdown handling
- ✅ Process monitoring and restart
- ✅ Centralized logging

**Trade-off**: Additional complexity. **Skip if not needed initially.**

---

### Step 5: Update docker-compose.yml

**File**: `docker-compose.yml`

Add MCP server service:

```yaml
services:
  # Existing AI service
  ai-service:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: ba-copilot-ai
    ports:
      - '8000:8000'
    environment:
      - OPEN_ROUTER_API_KEY=${OPEN_ROUTER_API_KEY}
      - FIGMA_API_TOKEN=${FIGMA_API_TOKEN}
      - DATABASE_URL=${DATABASE_URL:-postgresql://user:password@db:5432/ba_copilot}
      - MCP_SERVER_URL=http://mcp-server:3000 # NEW: Internal Docker network
    env_file:
      - .env
    volumes:
      - .:/app
    depends_on:
      mcp-server:
        condition: service_healthy # Wait for MCP to be healthy
      db:
        condition: service_started
    restart: unless-stopped
    networks:
      - ba-network

  # NEW: MCP Server service
  mcp-server:
    build:
      context: ./docker/mcp-server
      dockerfile: Dockerfile
    container_name: ba-copilot-mcp
    expose:
      - '3000' # Internal only, not published to host
    environment:
      - NODE_ENV=production
      - PORT=3000
    restart: unless-stopped
    networks:
      - ba-network
    healthcheck:
      test:
        [
          'CMD',
          'wget',
          '--quiet',
          '--tries=1',
          '--spider',
          'http://localhost:3000/health',
          '||',
          'exit',
          '1',
        ]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s

  # Existing database service
  db:
    image: postgres:15-alpine
    container_name: ba-copilot-db
    environment:
      - POSTGRES_USER=${POSTGRES_USER:-user}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-password}
      - POSTGRES_DB=${POSTGRES_DB:-ba_copilot}
    ports:
      - '5433:5432'
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - ba-network

networks:
  ba-network:
    driver: bridge

volumes:
  postgres_data:
```

**Key Configuration Explained**:

1. **Service Dependencies**

   ```yaml
   depends_on:
     mcp-server:
       condition: service_healthy
   ```

   - **Purpose**: Ensure MCP server is ready before FastAPI starts
   - **Condition**: `service_healthy` waits for health check to pass
   - **Why**: Prevent startup race conditions

2. **Internal Networking**

   ```yaml
   expose:
     - '3000' # Internal only
   ```

   - **expose** vs **ports**:
     - `expose`: Only accessible within Docker network
     - `ports`: Published to host machine
   - **Security**: MCP server not exposed to internet
   - **Access**: ai-service reaches via `http://mcp-server:3000`

3. **Docker Network DNS**

   ```yaml
   MCP_SERVER_URL=http://mcp-server:3000
   ```

   - **How it works**: Docker creates DNS entry for each service
   - **Service name = hostname**: `mcp-server` resolves to container IP
   - **Alternative**: Use IP address (not recommended, IPs change)

4. **Health Check Strategy**
   ```yaml
   healthcheck:
     test: ['CMD', 'wget', '--quiet', ...]
     interval: 30s
     start_period: 10s
   ```
   - **interval**: Check every 30 seconds
   - **start_period**: Grace period for startup
   - **retries**: Mark unhealthy after 3 failures
   - **Action**: Docker restarts if unhealthy (with `restart: unless-stopped`)

---

### Step 6: Update Environment Variables

**File**: `.env.example`

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

# MCP Server Configuration
# For Docker: use service name
MCP_SERVER_URL=http://mcp-server:3000
# For local development: use localhost
# MCP_SERVER_URL=http://localhost:3000
MCP_TIMEOUT=10
```

**File**: `.env` (your local file)

Update with appropriate values for your environment.

**Environment Strategy**:

| Environment    | MCP_SERVER_URL                | Why                          |
| -------------- | ----------------------------- | ---------------------------- |
| **Docker**     | `http://mcp-server:3000`      | Use Docker network DNS       |
| **Local Dev**  | `http://localhost:3000`       | Direct localhost connection  |
| **Production** | `http://mcp-service.internal` | Internal DNS or service mesh |

---

### Step 7: Build and Test MCP Server

```powershell
# Build MCP server image
docker-compose build mcp-server

# Expected output:
# [+] Building 45.2s (12/12) FINISHED
# => [internal] load build definition from Dockerfile
# => => transferring dockerfile: 789B
# ...
# => exporting to image
# => => exporting layers
# => => writing image sha256:abc123...
```

**Troubleshooting Build Issues**:

**Issue 1**: Package not found

```
ERROR: npm ERR! 404 Not Found - GET https://registry.npmjs.org/@rtuin/mcp-mermaid-validator
```

**Solution**: Verify package name and registry

```powershell
# Check npm registry
npm view @rtuin/mcp-mermaid-validator

# If package is in different registry, update Dockerfile:
RUN npm config set registry https://custom-registry.com
RUN npm install -g @rtuin/mcp-mermaid-validator
```

**Issue 2**: Build context too large

```
ERROR: failed to solve: error copying context: file size exceeds limit
```

**Solution**: Add `.dockerignore` in `docker/mcp-server/`:

```
node_modules
npm-debug.log
.git
.env
```

---

### Step 8: Start MCP Server Standalone

```powershell
# Start only MCP server
docker-compose up mcp-server

# Expected output:
# [+] Running 1/1
# ✔ Container ba-copilot-mcp  Created
# Attaching to ba-copilot-mcp
# ba-copilot-mcp  | Starting MCP Mermaid Validator...
# ba-copilot-mcp  | Server listening on http://0.0.0.0:3000
```

**Verify health check**:

```powershell
# Check container status
docker-compose ps

# Expected output:
# NAME                 STATUS                   PORTS
# ba-copilot-mcp       Up 30s (healthy)         3000/tcp
```

---

### Step 9: Test MCP Server from Host

Even though MCP server is not published to host, we can test via Docker exec:

```powershell
# Execute command inside container
docker exec ba-copilot-mcp wget -qO- --post-data='{"jsonrpc":"2.0","method":"tools/call","params":{"name":"validate_mermaid","arguments":{"code":"graph TD\nA-->B"}},"id":1}' --header="Content-Type: application/json" http://localhost:3000

# Expected output:
# {"jsonrpc":"2.0","result":{"content":[{"type":"text","text":"Valid Mermaid diagram"}]},"id":1}
```

**Alternative: Use docker-compose exec**:

```powershell
docker-compose exec mcp-server node -e "
const http = require('http');
const data = JSON.stringify({
  jsonrpc: '2.0',
  method: 'tools/call',
  params: {
    name: 'validate_mermaid',
    arguments: { code: 'graph TD\nA-->B' }
  },
  id: 1
});
const req = http.request({
  hostname: 'localhost',
  port: 3000,
  path: '/',
  method: 'POST',
  headers: { 'Content-Type': 'application/json' }
}, (res) => {
  let body = '';
  res.on('data', chunk => body += chunk);
  res.on('end', () => console.log(body));
});
req.write(data);
req.end();
"
```

---

### Step 10: Test Inter-Container Communication

Start both ai-service and mcp-server:

```powershell
# Start all services
docker-compose up -d

# Check all containers are healthy
docker-compose ps

# Expected output:
# NAME                 STATUS                   PORTS
# ba-copilot-ai        Up (healthy)             0.0.0.0:8000->8000/tcp
# ba-copilot-mcp       Up (healthy)             3000/tcp
# ba-copilot-db        Up                       0.0.0.0:5433->5432/tcp
```

**Test from ai-service container**:

```powershell
# Execute Python test inside ai-service container
docker-compose exec ai-service python -c "
import asyncio
from services.mcp_client import validate_mermaid_code

async def test():
    result = await validate_mermaid_code('graph TD\nA-->B')
    print(f'Validation result: {result}')

asyncio.run(test())
"

# Expected output:
# Validation result: {'valid': True, 'code': 'graph TD\nA-->B', 'errors': []}
```

---

### Step 11: Add Logging and Monitoring

**File**: `services/mcp_client.py` (update)

Enhance logging for production debugging:

```python
import logging
import os

# Configure structured logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

class MCPClient:
    # ... (existing code)

    async def validate_mermaid(self, code: str) -> Dict[str, Any]:
        """Validate Mermaid diagram syntax."""

        # Log request
        logger.info(f"Validating Mermaid code: {len(code)} characters")

        try:
            # ... (existing validation code)

            logger.info(f"Validation successful: valid={result['valid']}")
            return result

        except httpx.TimeoutException as e:
            logger.error(f"MCP server timeout: {e}", exc_info=True)
            raise MCPServerUnavailable(f"MCP server timeout after {self.timeout}s") from e

        except httpx.ConnectError as e:
            logger.error(f"Cannot connect to MCP server at {self.base_url}", exc_info=True)
            raise MCPServerUnavailable(f"Cannot connect to MCP server") from e
```

**Add monitoring metrics** (optional, for production):

```python
from datetime import datetime

class MCPMetrics:
    """Simple metrics collector for MCP client"""

    def __init__(self):
        self.total_requests = 0
        self.successful_validations = 0
        self.failed_validations = 0
        self.errors = 0
        self.total_latency = 0.0

    def record_success(self, latency: float):
        self.total_requests += 1
        self.successful_validations += 1
        self.total_latency += latency

    def record_failure(self, latency: float):
        self.total_requests += 1
        self.failed_validations += 1
        self.total_latency += latency

    def record_error(self):
        self.total_requests += 1
        self.errors += 1

    def get_stats(self) -> dict:
        return {
            "total_requests": self.total_requests,
            "successful_validations": self.successful_validations,
            "failed_validations": self.failed_validations,
            "errors": self.errors,
            "avg_latency": self.total_latency / max(self.total_requests, 1)
        }

# Global metrics instance
metrics = MCPMetrics()
```

---

## ✅ Verification Checklist

Before proceeding to Phase 3, ensure:

- [ ] `docker/mcp-server/Dockerfile` created
- [ ] `docker/mcp-server/package.json` created (optional)
- [ ] `docker-compose.yml` updated with mcp-server service
- [ ] `.env` and `.env.example` updated with MCP configuration
- [ ] MCP server builds successfully (`docker-compose build mcp-server`)
- [ ] MCP server starts and becomes healthy (`docker-compose up mcp-server`)
- [ ] Health check passes (`docker-compose ps` shows "healthy")
- [ ] Inter-container communication works (ai-service can reach mcp-server)
- [ ] Logging configured in `mcp_client.py`

---

## 🎯 Commit Time!

```powershell
# Stage all changes
git add docker/
git add docker-compose.yml
git add .env.example
git add services/mcp_client.py

# Commit with descriptive message
git commit -m "feat: configure MCP server with Docker integration

- Create Dockerfile for MCP Mermaid Validator server
- Add package.json for dependency management
- Update docker-compose.yml with mcp-server service
- Configure internal Docker networking (ba-network)
- Implement health checks for service dependencies
- Add logging and monitoring to MCP client
- Configure environment variables for Docker and local dev

Technical details:
- MCP server runs on internal port 3000
- Uses service_healthy condition for startup ordering
- Non-root user (mcp:1001) for security
- Alpine-based image for minimal footprint

Refs: #OPS-266"
```

---

## 🐛 Troubleshooting

### Issue: MCP server unhealthy

**Symptom**:

```
ba-copilot-mcp  | Health check failed
```

**Debug**:

```powershell
# Check MCP server logs
docker-compose logs mcp-server

# Check if process is running inside container
docker-compose exec mcp-server ps aux

# Manual health check
docker-compose exec mcp-server wget -qO- http://localhost:3000/health
```

**Solution**: Adjust health check endpoint or command.

### Issue: Cannot connect from ai-service to mcp-server

**Symptom**:

```python
MCPServerUnavailable: Cannot connect to MCP server at http://mcp-server:3000
```

**Debug**:

```powershell
# Check network connectivity
docker-compose exec ai-service ping mcp-server

# Check DNS resolution
docker-compose exec ai-service nslookup mcp-server

# Check if port is open
docker-compose exec ai-service nc -zv mcp-server 3000
```

**Solution**:

1. Ensure both services in same network (`ba-network`)
2. Verify `depends_on` is configured
3. Check firewall rules (if applicable)

### Issue: MCP server keeps restarting

**Symptom**:

```
ba-copilot-mcp  | Restarting...
ba-copilot-mcp  | Restarting...
```

**Debug**:

```powershell
# Check container logs
docker-compose logs --tail=50 mcp-server

# Check exit code
docker inspect ba-copilot-mcp | Select-String -Pattern "ExitCode"
```

**Common Causes**:

1. npm package installation failed
2. Port already in use inside container
3. Missing environment variables
4. Insufficient memory/CPU

---

## 📚 Additional Resources

- [Docker Compose Networking](https://docs.docker.com/compose/networking/)
- [Docker Health Checks](https://docs.docker.com/engine/reference/builder/#healthcheck)
- [Node.js Alpine Docker Best Practices](https://github.com/nodejs/docker-node/blob/main/docs/BestPractices.md)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)

---

**Next Phase**: [03_DOCKER_CONFIGURATION.md](./03_DOCKER_CONFIGURATION.md) →

---

**Phase 2 Complete** ✅  
**Est. Completion Time**: 25-30 minutes  
**Commit**: `feat: configure MCP server with Docker integration`
