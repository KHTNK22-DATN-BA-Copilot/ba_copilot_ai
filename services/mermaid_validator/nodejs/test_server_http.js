/**
 * HTTP Server Test Suite
 *
 * Tests the Express server endpoints via HTTP requests.
 * Run: node test_server_http.js
 */

const http = require('http');

// Configuration
const PORT = process.env.PORT || 51234;
const HOST = process.env.HOST || 'localhost';

const BASE_URL = `http://${HOST}:${PORT}`;

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
          code: 'graph TD\nA[Start\nB[End]',
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
