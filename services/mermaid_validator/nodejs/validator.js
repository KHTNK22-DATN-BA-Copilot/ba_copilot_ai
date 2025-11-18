/**
 * Mermaid Validation Logic
 *
 * Core validation functionality using @mermaid-js/mermaid-cli.
 *
 * @module validator
 */
const { execFile } = require('child_process');
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
  const TIMESTAMP = Date.now();
  const tempId = uuidv4();
  const tempDir = path.join(__dirname, 'temp');
  const inputFile = path.join(tempDir, `${tempId}.mmd`);
  const outputFile = path.join(tempDir, `${tempId}.png`);

  try {
    await fs.mkdir(tempDir, { recursive: true });
    await fs.writeFile(inputFile, code, 'utf8');

    // Use npx.cmd on Windows, npx on Unix
    const isWindows = process.platform === 'win32';
    const npxCommand = isWindows ? 'npx.cmd' : 'npx';

    await new Promise((resolve, reject) => {
      execFile(
        npxCommand,
        ['mmdc', '-i', inputFile, '-o', outputFile, '-q'],
        (error, stdout, stderr) => {
          if (error) return reject(stderr || error.message);
          resolve();
        }
      );
    });

    const result = {
      valid: true,
      code: code,
      diagram_type: detectDiagramType(code),
      timestamp: TIMESTAMP,
    };

    await cleanupFiles([inputFile, outputFile]);
    return result;
  } catch (error) {
    const result = {
      valid: false,
      code: code,
      errors: 'Errors caught from validator.js: ' + error,
      timestamp: TIMESTAMP,
    };

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
 * Clean up temporary files
 *
 * @param {Array<string>} files - File paths to delete
 */
async function cleanupFiles(files) {
  for (const file of files) {
    try {
      await fs.unlink(file);
    } catch (error) {
      // Silently ignore cleanup errors (file might not exist)
      // Only log if it's not a "file not found" error
      if (error.code !== 'ENOENT') {
        console.warn(`Failed to cleanup file ${file}:`, error.message);
      }
    }
  }
}

module.exports = {
  validateMermaid,
  detectDiagramType,
};
