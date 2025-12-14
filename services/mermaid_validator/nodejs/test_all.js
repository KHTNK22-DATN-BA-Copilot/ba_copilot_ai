/**
 * Validator
 *
 * Test simple tests and the Express server endpoints via HTTP requests.
 * Run: npm test
 */
const { spawn } = require('child_process');

console.log('Starting server...');
const server = spawn('node', ['server.js'], {
  cwd: __dirname,
  stdio: 'inherit',
});

setTimeout(() => {
  console.log('Running unit tests...');
  const unit = spawn('node', ['test_simple.js'], {
    cwd: __dirname,
    stdio: 'inherit',
  });
  unit.on('exit', (code) => {
    if (code !== 0) {
      console.error('Unit tests failed');
      server.kill();
      process.exit(code);
    }
    console.log('Running server tests...');
    const integration = spawn('node', ['test_server_http.js'], {
      cwd: __dirname,
      stdio: 'inherit',
    });
    integration.on('exit', (code2) => {
      server.kill();
      process.exit(code2);
    });
  });
}, 3000); // Wait for server to start (adjust if needed)
