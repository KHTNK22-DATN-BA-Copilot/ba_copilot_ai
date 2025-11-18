# Phase 2: Node.js Validator Service Implementation

## 🎯 Objective

Create a lightweight Express.js HTTP server that validates Mermaid diagram syntax using `@mermaid-js/mermaid-cli`.

**Estimated Time**: 45-60 minutes  
**Commit Message**: `feat: implement Node.js Express validation server`

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────┐
│         Node.js Validation Server                │
│         (Express.js on port 3001)                │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │  POST /validate                           │  │
│  │                                           │  │
│  │  Input: { code: "graph TD\nA-->B" }      │  │
│  │  Output: { valid: true/false, ... }      │  │
│  └──────────────────────────────────────────┘  │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │  GET /health                              │  │
│  │                                           │  │
│  │  Output: { status: "healthy", ... }      │  │
│  └──────────────────────────────────────────┘  │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │  Mermaid Validation Engine                │  │
│  │                                           │  │
│  │  - Parse diagram code                     │  │
│  │  - Detect syntax errors                   │  │
│  │  - Extract error messages                 │  │
│  └──────────────────────────────────────────┘  │
│                                                  │
└─────────────────────────────────────────────────┘
```

---

## 🔍 Design Decisions

### Validation Strategy

**Approach**: Use mermaid-cli's `parseMMD` function for syntax validation

```javascript
// Option 1: Full render (SLOW - 2-5 seconds)
await run(code, 'output.png', {}); // Renders to PNG

// Option 2: Parse only (FAST - 100-200ms) ✅ CHOSEN
const { parseMMD } = require('@mermaid-js/mermaid-cli');
await parseMMD(code); // Validates syntax only
```

**Performance Comparison**:

| Method      | Time      | Resource Usage            | Use Case             |
| ----------- | --------- | ------------------------- | -------------------- |
| Full Render | 2-5s      | High (Puppeteer + Chrome) | Image generation     |
| Parse Only  | 100-200ms | Low (V8 only)             | Syntax validation ✅ |

### Error Response Format

**Design**: Consistent JSON structure for success and failure

```javascript
// Success response
{
  "valid": true,
  "code": "graph TD\nA-->B",
  "diagram_type": "flowchart",
  "timestamp": 1699999999
}

// Error response
{
  "valid": false,
  "code": "graph TD\nA--INVALID-->B",
  "errors": [
    {
      "message": "Expecting 'SOLID_ARROW', got 'INVALID'",
      "line": 2,
      "column": 3
    }
  ],
  "timestamp": 1699999999
}
```

### Port Selection

**Decision**: Port 3001 (FastAPI uses 8000)

**Rationale**:

- ✅ Avoid conflicts with FastAPI (8000)
- ✅ Standard development port (3000 for React, 3001 for services)
- ✅ Easy to remember and document

---

## 🛠️ Implementation Steps

### Step 1: Create Server Entry Point

**File**: `services/mermaid_validator/nodejs/server.js`

```javascript
/**
 * Mermaid Validation Server
 *
 * Lightweight Express.js server for validating Mermaid diagram syntax.
 *
 * Architecture:
 *   - Express.js HTTP server
 *   - @mermaid-js/mermaid-cli for syntax validation
 *   - CORS enabled for development
 *   - Helmet for security headers
 *
 * Endpoints:
 *   POST /validate - Validate Mermaid diagram code
 *   GET /health - Health check endpoint
 *
 * Environment:
 *   PORT - Server port (default: 3001)
 *   NODE_ENV - Environment (development/production)
 *
 * @author BA Copilot Team
 * @version 1.0.0
 */

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const { validateMermaid } = require('./validator');

// Configuration
const PORT = process.env.PORT || 3001;
const HOST = process.env.HOST || 'localhost';
const NODE_ENV = process.env.NODE_ENV || 'development';

// Initialize Express app
const app = express();

// Middleware
app.use(helmet()); // Security headers
app.use(cors()); // Enable CORS
app.use(express.json({ limit: '1mb' })); // Parse JSON bodies

// Request logging middleware
app.use((req, res, next) => {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] ${req.method} ${req.path}`);
  next();
});

/**
 * POST /validate
 *
 * Validate Mermaid diagram syntax.
 *
 * Request Body:
 *   {
 *     "code": string  // Mermaid diagram code
 *   }
 *
 * Response:
 *   Success: { valid: true, code: string, diagram_type: string, timestamp: number }
 *   Error: { valid: false, code: string, errors: array, timestamp: number }
 *
 * Status Codes:
 *   200 - Validation completed (check 'valid' field)
 *   400 - Bad request (missing 'code' field)
 *   500 - Internal server error
 */
app.post('/validate', async (req, res) => {
  const startTime = Date.now();

  try {
    const { code } = req.body;

    // Validate input
    if (!code) {
      return res.status(400).json({
        valid: false,
        error: 'Missing required field: code',
        timestamp: Date.now(),
      });
    }

    if (typeof code !== 'string') {
      return res.status(400).json({
        valid: false,
        error: 'Field "code" must be a string',
        timestamp: Date.now(),
      });
    }

    // Validate Mermaid code
    const result = await validateMermaid(code);

    // Add timing information
    const duration = Date.now() - startTime;
    result.duration_ms = duration;

    console.log(
      `Validation completed in ${duration}ms - valid: ${result.valid}`
    );

    res.json(result);
  } catch (error) {
    console.error('Validation error:', error);

    res.status(500).json({
      valid: false,
      error: 'Internal server error',
      message: error.message,
      timestamp: Date.now(),
    });
  }
});

/**
 * GET /health
 *
 * Health check endpoint for monitoring.
 *
 * Response:
 *   {
 *     "status": "healthy",
 *     "timestamp": number,
 *     "uptime": number,
 *     "environment": string,
 *     "version": string
 *   }
 *
 * Status Codes:
 *   200 - Server is healthy
 */
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: Date.now(),
    uptime: process.uptime(),
    environment: NODE_ENV,
    version: '1.0.0',
    memory: {
      used: Math.round(process.memoryUsage().heapUsed / 1024 / 1024),
      total: Math.round(process.memoryUsage().heapTotal / 1024 / 1024),
      unit: 'MB',
    },
  });
});

/**
 * GET /
 *
 * Root endpoint - API information
 */
app.get('/', (req, res) => {
  res.json({
    name: 'Mermaid Validation Service',
    version: '1.0.0',
    endpoints: {
      validate: 'POST /validate',
      health: 'GET /health',
    },
    documentation: 'https://github.com/your-org/ba_copilot_ai',
  });
});

/**
 * 404 handler
 */
app.use((req, res) => {
  res.status(404).json({
    error: 'Not Found',
    message: `Cannot ${req.method} ${req.path}`,
    available_endpoints: ['POST /validate', 'GET /health', 'GET /'],
  });
});

/**
 * Error handler
 */
app.use((err, req, res, next) => {
  console.error('Unhandled error:', err);

  res.status(500).json({
    error: 'Internal Server Error',
    message: NODE_ENV === 'development' ? err.message : 'An error occurred',
    timestamp: Date.now(),
  });
});

/**
 * Start server
 */
const server = app.listen(PORT, HOST, () => {
  console.log('='.repeat(60));
  console.log('  Mermaid Validation Server');
  console.log('='.repeat(60));
  console.log(`  Status: RUNNING`);
  console.log(`  URL: http://${HOST}:${PORT}`);
  console.log(`  Environment: ${NODE_ENV}`);
  console.log(`  Process ID: ${process.pid}`);
  console.log('='.repeat(60));
  console.log('  Endpoints:');
  console.log(`    POST /validate - Validate Mermaid diagrams`);
  console.log(`    GET /health - Health check`);
  console.log('='.repeat(60));
});

/**
 * Graceful shutdown handler
 */
const gracefulShutdown = (signal) => {
  console.log(`\n${signal} received. Shutting down gracefully...`);

  server.close(() => {
    console.log('Server closed. Exiting process.');
    process.exit(0);
  });

  // Force exit after 10 seconds
  setTimeout(() => {
    console.error('Forced shutdown after timeout');
    process.exit(1);
  }, 10000);
};

process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

// Export for testing
module.exports = app;
```

---

### Step 2: Create Validation Logic

**File**: `services/mermaid_validator/nodejs/validator.js`

```javascript
/**
 * Mermaid Validation Logic
 *
 * Core validation functionality using @mermaid-js/mermaid-cli.
 *
 * @module validator
 */

const { run } = require('@mermaid-js/mermaid-cli');
const fs = require('fs').promises;
const path = require('path');
const { v4: uuidv4 } = require('uuid');

/**
 * Validate Mermaid diagram code
 *
 * Strategy:
 *   1. Create temporary file with diagram code
 *   2. Attempt to parse with mermaid-cli
 *   3. Return validation result
 *   4. Clean up temporary file
 *
 * @param {string} code - Mermaid diagram code
 * @returns {Promise<Object>} Validation result
 */
async function validateMermaid(code) {
  const timestamp = Date.now();

  // Create temporary input file
  const tempId = uuidv4();
  const tempDir = path.join(__dirname, 'temp');
  const inputFile = path.join(tempDir, `${tempId}.mmd`);
  const outputFile = path.join(tempDir, `${tempId}.png`);

  try {
    // Ensure temp directory exists
    await fs.mkdir(tempDir, { recursive: true });

    // Write Mermaid code to temp file
    await fs.writeFile(inputFile, code, 'utf8');

    // Attempt to run mermaid-cli (this validates syntax)
    await run(inputFile, outputFile, {
      quiet: true,
      outputFormat: 'png',
      parseMMDOptions: {
        suppressErrors: false,
      },
    });

    // If we reach here, diagram is valid
    const result = {
      valid: true,
      code: code,
      diagram_type: detectDiagramType(code),
      timestamp: timestamp,
    };

    // Clean up
    await cleanupFiles([inputFile, outputFile]);

    return result;
  } catch (error) {
    // Validation failed - extract error details
    const result = {
      valid: false,
      code: code,
      errors: parseErrors(error),
      timestamp: timestamp,
    };

    // Clean up
    await cleanupFiles([inputFile, outputFile]);

    return result;
  }
}

/**
 * Detect diagram type from code
 *
 * @param {string} code - Mermaid code
 * @returns {string} Diagram type
 */
function detectDiagramType(code) {
  const firstLine = code.trim().split('\n')[0].toLowerCase();

  if (firstLine.includes('classDiagram')) return 'class';
  if (firstLine.includes('sequenceDiagram')) return 'sequence';
  if (firstLine.includes('erDiagram')) return 'er';
  if (firstLine.includes('flowchart') || firstLine.includes('graph'))
    return 'flowchart';
  if (firstLine.includes('gantt')) return 'gantt';
  if (firstLine.includes('pie')) return 'pie';
  if (firstLine.includes('stateDiagram')) return 'state';
  if (firstLine.includes('journey')) return 'journey';

  return 'unknown';
}

/**
 * Parse error object into structured format
 *
 * @param {Error} error - Error from mermaid-cli
 * @returns {Array} Array of error objects
 */
function parseErrors(error) {
  const errors = [];

  // Extract error message
  let message = error.message || 'Unknown error';

  // Try to extract line/column information
  const lineMatch = message.match(/line (\d+)/i);
  const columnMatch = message.match(/column (\d+)/i);

  const errorObj = {
    message: cleanErrorMessage(message),
    type: error.name || 'ValidationError',
  };

  if (lineMatch) {
    errorObj.line = parseInt(lineMatch[1]);
  }

  if (columnMatch) {
    errorObj.column = parseInt(columnMatch[1]);
  }

  errors.push(errorObj);

  return errors;
}

/**
 * Clean error message (remove technical details)
 *
 * @param {string} message - Raw error message
 * @returns {string} Cleaned message
 */
function cleanErrorMessage(message) {
  // Remove file paths
  message = message.replace(/\/tmp\/[^\s]+/g, '');
  message = message.replace(/[A-Z]:\\[^\s]+/g, '');

  // Remove stack traces
  message = message.split('\n')[0];

  // Trim whitespace
  message = message.trim();

  return message;
}

/**
 * Clean up temporary files
 *
 * @param {Array<string>} files - File paths to delete
 */
async function cleanupFiles(files) {
  for (const file of files) {
    try {
      await fs.unlink(file);
    } catch (error) {
      // Ignore cleanup errors
      console.warn(`Failed to cleanup file ${file}:`, error.message);
    }
  }
}

/**
 * Validate multiple diagrams in batch
 *
 * @param {Array<string>} codes - Array of Mermaid codes
 * @returns {Promise<Array>} Array of validation results
 */
async function validateBatch(codes) {
  const promises = codes.map((code) => validateMermaid(code));
  return Promise.all(promises);
}

module.exports = {
  validateMermaid,
  validateBatch,
  detectDiagramType,
};
```

**Note**: We need to install `uuid` package:

```powershell
cd services\mermaid_validator\nodejs
npm install uuid@9.0.1
```

---

### Step 3: Create Test Script

**File**: `services/mermaid_validator/nodejs/test.js`

```javascript
/**
 * Simple test script for validation server
 *
 * Run: node test.js
 */

const { validateMermaid } = require('./validator');

// Test cases
const testCases = [
  {
    name: 'Valid Class Diagram',
    code: `classDiagram
    class User {
        +String name
        +String email
        +login()
    }`,
    expectedValid: true,
  },
  {
    name: 'Valid Flowchart',
    code: `graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Process]
    B -->|No| D[End]`,
    expectedValid: true,
  },
  {
    name: 'Invalid Syntax',
    code: `graph TD
    A--INVALID-->B`,
    expectedValid: false,
  },
  {
    name: 'Empty Code',
    code: '',
    expectedValid: false,
  },
  {
    name: 'Unknown Keyword',
    code: `classDiagra
    class User`,
    expectedValid: false,
  },
];

async function runTests() {
  console.log('='.repeat(60));
  console.log('  Mermaid Validator Test Suite');
  console.log('='.repeat(60));

  let passed = 0;
  let failed = 0;

  for (const testCase of testCases) {
    console.log(`\nTest: ${testCase.name}`);
    console.log('-'.repeat(60));

    try {
      const result = await validateMermaid(testCase.code);

      const success = result.valid === testCase.expectedValid;

      if (success) {
        console.log(`✓ PASS - valid: ${result.valid}`);
        passed++;
      } else {
        console.log(
          `✗ FAIL - Expected valid: ${testCase.expectedValid}, got: ${result.valid}`
        );
        failed++;
      }

      if (!result.valid && result.errors) {
        console.log(`  Errors: ${JSON.stringify(result.errors, null, 2)}`);
      }
    } catch (error) {
      console.log(`✗ ERROR - ${error.message}`);
      failed++;
    }
  }

  console.log('\n' + '='.repeat(60));
  console.log(`  Results: ${passed} passed, ${failed} failed`);
  console.log('='.repeat(60));

  process.exit(failed > 0 ? 1 : 0);
}

runTests().catch((error) => {
  console.error('Test suite error:', error);
  process.exit(1);
});
```

**Run tests**:

```powershell
cd services\mermaid_validator\nodejs
node test.js
```

---

### Step 4: Create Environment Configuration

**File**: `services/mermaid_validator/nodejs/.env.example`

```bash
# Server Configuration
PORT=3001
HOST=localhost
NODE_ENV=development

# Logging
LOG_LEVEL=info

# Performance
REQUEST_TIMEOUT=10000
MAX_REQUEST_SIZE=1048576

# Puppeteer (for mermaid-cli)
PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser
PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=false
```

---

### Step 5: Update package.json

Update scripts and metadata:

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
    "test:watch": "nodemon --exec 'node test.js'",
    "health": "curl http://localhost:3001/health",
    "validate": "curl -X POST http://localhost:3001/validate -H 'Content-Type: application/json' -d '{\"code\":\"graph TD\\nA-->B\"}'"
  },
  "engines": {
    "node": ">=18.0.0",
    "npm": ">=9.0.0"
  },
  "keywords": ["mermaid", "validation", "diagrams", "uml", "express"],
  "author": "BA Copilot Team",
  "license": "MIT",
  "dependencies": {
    "@mermaid-js/mermaid-cli": "^10.6.1",
    "cors": "^2.8.5",
    "express": "^4.18.2",
    "helmet": "^7.1.0",
    "uuid": "^9.0.1"
  },
  "devDependencies": {
    "nodemon": "^3.0.2"
  }
}
```

---

### Step 6: Test the Server Locally

**Terminal 1 - Start Server**:

```powershell
cd d:\Do_an_tot_nghiep\ba_copilot_ai\services\mermaid_validator\nodejs
node server.js
```

**Expected Output**:

```
============================================================
  Mermaid Validation Server
============================================================
  Status: RUNNING
  URL: http://localhost:3001
  Environment: development
  Process ID: 12345
============================================================
  Endpoints:
    POST /validate - Validate Mermaid diagrams
    GET /health - Health check
============================================================
```

**Terminal 2 - Test Health Endpoint**:

```powershell
# Test health check
Invoke-RestMethod -Uri "http://localhost:3001/health" -Method Get
```

**Expected Response**:

```json
{
  "status": "healthy",
  "timestamp": 1699999999,
  "uptime": 12.345,
  "environment": "development",
  "version": "1.0.0",
  "memory": {
    "used": 45,
    "total": 128,
    "unit": "MB"
  }
}
```

**Terminal 2 - Test Validation (Valid)**:

```powershell
$body = @{
    code = "graph TD`nA-->B`nB-->C"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:3001/validate" `
                  -Method Post `
                  -Body $body `
                  -ContentType "application/json"
```

**Expected Response**:

```json
{
  "valid": true,
  "code": "graph TD\nA-->B\nB-->C",
  "diagram_type": "flowchart",
  "timestamp": 1699999999,
  "duration_ms": 156
}
```

**Terminal 2 - Test Validation (Invalid)**:

```powershell
$body = @{
    code = "graph TD`nA--INVALID-->B"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:3001/validate" `
                  -Method Post `
                  -Body $body `
                  -ContentType "application/json"
```

**Expected Response**:

```json
{
  "valid": false,
  "code": "graph TD\nA--INVALID-->B",
  "errors": [
    {
      "message": "Parse error on line 2: Expecting 'SOLID_ARROW', got 'INVALID'",
      "type": "ValidationError",
      "line": 2
    }
  ],
  "timestamp": 1699999999,
  "duration_ms": 89
}
```

---

### Step 7: Create Comprehensive Test Suite

**File**: `services/mermaid_validator/nodejs/test-server.js`

```javascript
/**
 * HTTP Server Test Suite
 *
 * Tests the Express server endpoints via HTTP requests.
 * Run: node test-server.js
 */

const http = require('http');

const BASE_URL = 'http://localhost:3001';

/**
 * Make HTTP request
 */
function request(method, path, body = null) {
  return new Promise((resolve, reject) => {
    const url = new URL(path, BASE_URL);

    const options = {
      hostname: url.hostname,
      port: url.port,
      path: url.pathname,
      method: method,
      headers: {
        'Content-Type': 'application/json',
      },
    };

    const req = http.request(options, (res) => {
      let data = '';

      res.on('data', (chunk) => {
        data += chunk;
      });

      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          resolve({ status: res.statusCode, data: parsed });
        } catch (error) {
          resolve({ status: res.statusCode, data: data });
        }
      });
    });

    req.on('error', reject);

    if (body) {
      req.write(JSON.stringify(body));
    }

    req.end();
  });
}

/**
 * Test suite
 */
async function runTests() {
  console.log('='.repeat(60));
  console.log('  HTTP Server Test Suite');
  console.log('='.repeat(60));

  const tests = [
    {
      name: 'GET / - Root endpoint',
      run: async () => {
        const res = await request('GET', '/');
        return (
          res.status === 200 && res.data.name === 'Mermaid Validation Service'
        );
      },
    },
    {
      name: 'GET /health - Health check',
      run: async () => {
        const res = await request('GET', '/health');
        return res.status === 200 && res.data.status === 'healthy';
      },
    },
    {
      name: 'POST /validate - Valid diagram',
      run: async () => {
        const res = await request('POST', '/validate', {
          code: 'graph TD\nA-->B',
        });
        return res.status === 200 && res.data.valid === true;
      },
    },
    {
      name: 'POST /validate - Invalid diagram',
      run: async () => {
        const res = await request('POST', '/validate', {
          code: 'graph TD\nA--INVALID-->B',
        });
        return res.status === 200 && res.data.valid === false;
      },
    },
    {
      name: 'POST /validate - Missing code',
      run: async () => {
        const res = await request('POST', '/validate', {});
        return res.status === 400;
      },
    },
    {
      name: 'POST /validate - Invalid code type',
      run: async () => {
        const res = await request('POST', '/validate', {
          code: 123,
        });
        return res.status === 400;
      },
    },
    {
      name: 'GET /invalid - 404 error',
      run: async () => {
        const res = await request('GET', '/invalid');
        return res.status === 404;
      },
    },
  ];

  let passed = 0;
  let failed = 0;

  for (const test of tests) {
    try {
      const result = await test.run();

      if (result) {
        console.log(`✓ PASS - ${test.name}`);
        passed++;
      } else {
        console.log(`✗ FAIL - ${test.name}`);
        failed++;
      }
    } catch (error) {
      console.log(`✗ ERROR - ${test.name}: ${error.message}`);
      failed++;
    }
  }

  console.log('\n' + '='.repeat(60));
  console.log(`  Results: ${passed} passed, ${failed} failed`);
  console.log('='.repeat(60));

  process.exit(failed > 0 ? 1 : 0);
}

// Wait for server to start
setTimeout(() => {
  runTests().catch((error) => {
    console.error('Test suite error:', error);
    process.exit(1);
  });
}, 1000);
```

**Run server tests**:

```powershell
# Terminal 1: Start server
cd services\mermaid_validator\nodejs
node server.js

# Terminal 2: Run tests
npm run test-server
```

---

## ✅ Verification Checklist

Before proceeding to Phase 3, ensure:

- [ ] `server.js` created with Express app
- [ ] `validator.js` created with validation logic
- [ ] `test.js` runs successfully
- [ ] `test-server.js` runs successfully
- [ ] Server starts on port 3001
- [ ] Health endpoint returns 200 OK
- [ ] Validation endpoint accepts valid Mermaid
- [ ] Validation endpoint rejects invalid Mermaid
- [ ] Error messages are clear and actionable
- [ ] Server logs requests and responses
- [ ] Graceful shutdown works (Ctrl+C)

---

## 🎯 Commit Time!

```powershell
# Navigate to ba_copilot_ai root
cd d:\Do_an_tot_nghiep\ba_copilot_ai

# Stage changes
git add services/mermaid_validator/nodejs/

# Commit
git commit -m "feat: implement Node.js Express validation server

- Create Express.js server on port 3001
- Implement POST /validate endpoint for Mermaid validation
- Add GET /health endpoint for monitoring
- Create validation logic using @mermaid-js/mermaid-cli
- Add error parsing and structured responses
- Implement graceful shutdown handling
- Create comprehensive test suites

Features:
  - Fast syntax-only validation (100-200ms)
  - Detailed error messages with line/column info
  - Memory and uptime monitoring
  - CORS and security headers (helmet)
  - Request logging and performance metrics

Files:
  - server.js: Express HTTP server
  - validator.js: Mermaid validation logic
  - test.js: Unit tests
  - test-server.js: HTTP integration tests
  - .env.example: Configuration template

Refs: #OPS-317"
```

---

## 🐛 Troubleshooting

### Issue: Puppeteer installation fails

**Symptom**:

```
Error: Failed to download Chromium
```

**Solution**:

```powershell
# Option 1: Skip Chromium download (use system Chrome)
$env:PUPPETEER_SKIP_CHROMIUM_DOWNLOAD="true"
npm install

# Option 2: Specify Chromium path
$env:PUPPETEER_EXECUTABLE_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"
npm install
```

### Issue: Server won't start - port in use

**Symptom**:

```
Error: listen EADDRINUSE: address already in use :::3001
```

**Solution**:

```powershell
# Find process using port 3001
Get-Process -Id (Get-NetTCPConnection -LocalPort 3001).OwningProcess

# Kill process
Stop-Process -Id <PID> -Force

# Or use different port
$env:PORT=3002
node server.js
```

### Issue: Validation always fails

**Symptom**:

```
{ valid: false, errors: [...] }
```

**Debug**:

```javascript
// Add debug logging to validator.js
console.log('Input code:', code);
console.log('Temp file:', inputFile);

// Check temp directory permissions
await fs.access(tempDir, fs.constants.W_OK);
```

---

## 📚 Additional Resources

- [Express.js Error Handling](https://expressjs.com/en/guide/error-handling.html)
- [@mermaid-js/mermaid-cli API](https://github.com/mermaid-js/mermaid-cli/blob/master/docs/api.md)
- [Puppeteer Configuration](https://pptr.dev/guides/configuration)
- [Node.js HTTP Server](https://nodejs.org/api/http.html)

---

**Next Phase**: [03_PYTHON_SUBPROCESS_MANAGER.md](./03_PYTHON_SUBPROCESS_MANAGER.md) →

---

**Phase 2 Complete** ✅  
**Est. Completion Time**: 45-60 minutes  
**Commit**: `feat: implement Node.js Express validation server`
