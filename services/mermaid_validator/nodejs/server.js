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

const crypto = require('crypto');
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const { validateMermaid } = require('./validator');

// Response cache for identical diagrams (max 100 entries, 10 min TTL)
const CACHE_MAX_SIZE = 100;
const CACHE_TTL_MS = 10 * 60 * 1000; // 10 minutes
const responseCache = new Map();

// Request rate limiting (max 10 concurrent validations)
let activeValidations = 0;
const MAX_CONCURRENT = 10;

// Configuration
const PORT = process.env.PORT || 51234;
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

    // Check cache first
    const codeHash = crypto.createHash('md5').update(code).digest('hex');
    const cached = responseCache.get(codeHash);
    if (cached && Date.now() - cached.timestamp < CACHE_TTL_MS) {
      console.log(
        `[CACHE HIT] Returning cached result (${Date.now() - startTime}ms)`
      );
      return res.json({
        ...cached.result,
        cached: true,
        duration_ms: Date.now() - startTime,
      });
    }

    // Rate limiting
    if (activeValidations >= MAX_CONCURRENT) {
      return res.status(429).json({
        valid: false,
        error: 'Too many concurrent validations. Please retry later.',
        active_count: activeValidations,
        timestamp: Date.now(),
      });
    }

    activeValidations++;

    // Validate Mermaid code
    const result = await validateMermaid(code);

    // Cache successful validations
    if (result.valid) {
      responseCache.set(codeHash, { result, timestamp: Date.now() });

      // Evict oldest entry if cache is full
      if (responseCache.size > CACHE_MAX_SIZE) {
        const firstKey = responseCache.keys().next().value;
        responseCache.delete(firstKey);
      }
    }

    // Add timing information
    const duration = Date.now() - startTime;
    result.duration_ms = duration;

    console.log(
      `[${result.valid ? 'PASS' : 'FAIL'}] ${
        result.diagram_type || 'unknown'
      } (${duration}ms)`
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
  } finally {
    activeValidations--;
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
    name: 'Mermaid Validation Service',
    version: '1.0.0',
    endpoints: {
      validate: 'POST /validate',
      health: 'GET /health',
    },
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
    documentation: 'https://github.com/KHTNK22-DATN-BA-Copilot/ba_copilot_ai',
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
