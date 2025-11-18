/**
 * Simple test script for validation server
 *
 * Run: node test_simple.js
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
    A[Start
    B[End]`,
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
