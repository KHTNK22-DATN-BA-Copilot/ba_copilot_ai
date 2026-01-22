# Integration Testing Guide

## BA Copilot AI Service - Document Constraint Validation

**Version:** 1.0  
**Date:** January 21, 2026  
**Scope:** Testing document constraint validation between Backend and AI services

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Environment Setup](#environment-setup)
4. [Running Unit Tests](#running-unit-tests)
5. [Integration Testing with Backend](#integration-testing-with-backend)
6. [Test Scenarios](#test-scenarios)
7. [Expected Responses](#expected-responses)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The Document Constraint System ensures AI-generated documents are produced in the correct order following SDLC best practices. This guide covers testing the constraint validation between the AI service and Backend.

### Architecture Summary

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend   │────▶│ AI Service  │
└─────────────┘     └─────────────┘     └─────────────┘
                          │                    │
                    Validates              Validates
                    constraints         prerequisites
                    (enforcement)       (content check)
                          │                    │
                          ▼                    ▼
                    ┌─────────────┐     ┌─────────────┐
                    │  Database   │     │   LLM API   │
                    │  (Supabase) │     │ (OpenRouter)│
                    └─────────────┘     └─────────────┘
```

### Responsibility Split

| Component      | Responsibility                                                               |
| -------------- | ---------------------------------------------------------------------------- |
| **Backend**    | Enforce constraints, fetch prerequisite files, provide `storage_paths` to AI |
| **AI Service** | Validate that expected content was loaded, generate documents with context   |

---

## Prerequisites

### Software Requirements

- Python 3.11+
- Docker & Docker Compose
- Node.js 18+ (for Mermaid validator)
- Git

### Environment Variables

Create `.env` file in `ba_copilot_ai/`:

```bash
# Required for AI generation
OPEN_ROUTER_API_KEY=your_openrouter_api_key

# Supabase (for get_content_file integration)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Optional
LOG_LEVEL=INFO
```

---

## Environment Setup

### Option 1: Docker (Recommended)

```bash
# From ba_copilot_ai directory
cd ba_copilot_ai

# Build and start services
docker-compose up --build

# Verify service is running
curl http://localhost:8001/health
```

### Option 2: Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Start the service
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

---

## Running Unit Tests

### All Constraint Validation Tests

```bash
# Run from ba_copilot_ai directory
pytest tests/test_constraint_validation.py -v

# With coverage
pytest tests/test_constraint_validation.py -v --cov=services --cov=workflows/nodes

# Specific test class
pytest tests/test_constraint_validation.py::TestValidatePrerequisites -v

# Specific test
pytest tests/test_constraint_validation.py::TestValidatePrerequisites::test_required_prerequisites_missing_strict_raises -v
```

### Expected Output

```
========================= test session starts ==========================
tests/test_constraint_validation.py::TestDocumentConstraintsCompleteness::test_all_document_types_defined PASSED
tests/test_constraint_validation.py::TestDocumentConstraintsCompleteness::test_constraint_structure PASSED
tests/test_constraint_validation.py::TestDocumentConstraintsCompleteness::test_no_self_reference PASSED
...
========================= 40+ passed in X.XXs ==========================
```

---

## Integration Testing with Backend

### Step 1: Start Both Services

```bash
# Terminal 1: Start AI Service
cd ba_copilot_ai
docker-compose up

# Terminal 2: Start Backend Service
cd ba_copilot_backend
docker-compose up
```

### Step 2: Upload Prerequisite Files via Backend

Before generating documents with prerequisites, upload the required files:

```bash
# Upload high-level-requirements.md to a project
curl -X POST "http://localhost:8000/api/v1/files/upload" \
  -H "Authorization: Bearer <token>" \
  -F "file=@high-level-requirements.md" \
  -F "project_id=<project_id>" \
  -F "folder_id=<folder_id>"
```

### Step 3: Generate Document with Prerequisites

```bash
# Backend calls AI service internally with storage_paths
curl -X POST "http://localhost:8000/api/v1/design/hld-arch/generate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "message": "Create high-level architecture for e-commerce system",
    "project_id": "<project_id>"
  }'
```

### Step 4: Direct AI Service Testing (Bypass Backend)

For testing AI service directly:

```bash
# Entry point document (no prerequisites required)
curl -X POST "http://localhost:8001/api/v1/planning/stakeholder-register/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create stakeholder register for hospital management system"
  }'

# Document with prerequisites - simulate Backend providing context
curl -X POST "http://localhost:8001/api/v1/design/hld-arch/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create high-level architecture",
    "storage_paths": ["/1/2/high-level-requirements.md", "/1/2/scope-statement.md"],
    "document_type": "hld-arch"
  }'
```

---

## Test Scenarios

### Happy Path: All Prerequisites Met

**Scenario:** Generate `hld-arch` with all required prerequisites provided.

**Input:**

```json
{
  "message": "Create high-level architecture for task management app",
  "storage_paths": [
    "/project/high-level-requirements.md",
    "/project/scope-statement.md"
  ],
  "document_type": "hld-arch"
}
```

**Expected Behavior:**

- Validation passes
- AI generates architecture document with context from prerequisites
- Response includes generated content

**Logs Expected:**

```
INFO: Validating prerequisites for 'hld-arch'
INFO: ✅ Prerequisites validated for 'hld-arch'. Found: ['high-level-requirements', 'scope-statement']
```

---

### Happy Path: Entry Point Document

**Scenario:** Generate `stakeholder-register` (no prerequisites required).

**Input:**

```json
{
  "message": "Create stakeholder register for mobile banking app"
}
```

**Expected Behavior:**

- No validation needed (entry point)
- AI generates document
- Response includes generated content

---

### Edge Case: Missing Required Prerequisites (Non-Strict)

**Scenario:** Generate `hld-arch` without providing required files (default mode).

**Input:**

```json
{
  "message": "Create high-level architecture",
  "storage_paths": [],
  "document_type": "hld-arch"
}
```

**Expected Behavior:**

- Validation sets `valid: false`
- Generation proceeds with warning logged
- Response includes generated content (lower quality expected)

**Logs Expected:**

```
ERROR: Missing required prerequisites for 'hld-arch': high-level-requirements, scope-statement. Backend should have validated these before calling AI service.
```

---

### Edge Case: Partial Prerequisites

**Scenario:** Generate `lld-api` with only some required prerequisites.

**Required:** `hld-arch`, `high-level-requirements`  
**Provided:** Only `hld-arch`

**Input:**

```json
{
  "message": "Create API specification",
  "storage_paths": ["/project/hld-arch.md"],
  "document_type": "lld-api"
}
```

**Expected Behavior:**

- Validation fails (missing `high-level-requirements`)
- Generation proceeds with warning
- Log indicates which prerequisites are missing

---

### Edge Case: Recommended But Not Required

**Scenario:** Generate `activity-diagram` with required but without recommended.

**Required:** `high-level-requirements` ✓  
**Recommended:** `scope-statement`, `usecase-diagram` ✗

**Input:**

```json
{
  "message": "Create activity diagram for checkout process",
  "storage_paths": ["/project/high-level-requirements.md"],
  "document_type": "activity-diagram"
}
```

**Expected Behavior:**

- Validation passes (`valid: true`)
- Log notes missing recommended documents
- Generation proceeds normally

**Logs Expected:**

```
INFO: ✅ Prerequisites validated for 'activity-diagram'. Found: ['high-level-requirements']
INFO: ℹ️ Recommended prerequisites not provided: ['scope-statement', 'usecase-diagram']
```

---

### Edge Case: Unknown Document Type

**Scenario:** Request generation for an undefined document type.

**Input:**

```json
{
  "message": "Generate something",
  "document_type": "unknown-custom-doc"
}
```

**Expected Behavior:**

- Validation passes with warning
- Log indicates no constraints defined
- Generation proceeds (endpoint may not exist)

---

### Edge Case: File Content Detection

**Scenario:** Prerequisites identified from file content rather than paths.

**Input:**

```json
{
  "message": "Create HLD architecture",
  "storage_paths": [],
  "document_type": "hld-arch"
}
```

**Pre-populated State** (simulating `get_content_file` output):

```python
{
  "extracted_text": """
  ### File: high-level-requirements.md
  The system shall support user authentication...

  ### File: scope-statement.md
  Project scope includes web and mobile platforms...
  """
}
```

**Expected Behavior:**

- Validation detects documents from `### File:` markers
- Validation passes
- Generation uses extracted context

---

## Expected Responses

### Successful Generation Response

```json
{
  "type": "hld-arch",
  "response": {
    "title": "High-Level Architecture Design",
    "overview": "...",
    "components": "...",
    "detail": "# High-Level Architecture Design\n\n## Overview\n..."
  }
}
```

### Validation Error (If Strict Mode Enabled)

```json
{
  "detail": "Missing required prerequisites for 'hld-arch': high-level-requirements, scope-statement"
}
```

HTTP Status: `500` (or `422` if Backend propagates validation error)

---

## Manual Testing Checklist

### Unit Test Verification

- [ ] Run `pytest tests/test_constraint_validation.py -v`
- [ ] All tests pass
- [ ] No import errors

### Docker Verification

- [ ] `docker-compose build` succeeds
- [ ] `docker-compose up` starts without errors
- [ ] Health endpoint responds: `curl localhost:8001/health`

### Integration Verification

- [ ] Entry point document generates without prerequisites
- [ ] Document with prerequisites generates with context
- [ ] Missing prerequisites logs appropriate warnings
- [ ] Constraint validation result appears in logs

---

## Troubleshooting

### Import Errors

**Symptom:** `ModuleNotFoundError: No module named 'services.constraint_validator'`

**Solution:**

```bash
# Ensure you're in the ba_copilot_ai directory
cd ba_copilot_ai
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/test_constraint_validation.py -v
```

### OpenRouter API Key Missing

**Symptom:** Health check shows `"openrouter_api_configured": false`

**Solution:**

```bash
# Set environment variable
export OPEN_ROUTER_API_KEY=your_key_here

# Or add to .env file
echo "OPEN_ROUTER_API_KEY=your_key" >> .env
```

### Mermaid Validator Not Ready

**Symptom:** Logs show "⚠️ Validator not ready"

**Solution:**

```bash
# Ensure mermaid-cli is available
cd services/mermaid_validator/nodejs
npm install

# Or use Docker which handles this automatically
docker-compose up --build
```

### Test Failures Due to Logging

**Symptom:** Tests fail with logging-related assertions

**Solution:**

```bash
# Run with explicit log capture
pytest tests/test_constraint_validation.py -v --log-cli-level=DEBUG
```

---

## Test Data Fixtures

For integration tests requiring actual file content, create test fixtures:

### Sample high-level-requirements.md

```markdown
# High-Level Requirements

## Functional Requirements

- FR-001: User registration and authentication
- FR-002: Product catalog browsing
- FR-003: Shopping cart management

## Non-Functional Requirements

- NFR-001: Response time < 2 seconds
- NFR-002: 99.9% uptime SLA
```

### Sample scope-statement.md

```markdown
# Project Scope Statement

## In Scope

- Web application development
- Mobile responsive design
- Payment integration

## Out of Scope

- Hardware procurement
- Physical store integration
```

### Sample hld-arch.md

```markdown
# High-Level Architecture

## System Overview

Three-tier architecture with React frontend, FastAPI backend, PostgreSQL database.

## Components

- Frontend: React + TypeScript
- API Gateway: FastAPI
- Database: PostgreSQL + Supabase
- Cache: Redis
```

---

## Future Enhancements

1. **Automated Integration Tests**: Once file upload mocking is available
2. **Performance Benchmarks**: Measure validation overhead
3. **Constraint Override Testing**: Test GUIDED mode override flows
4. **Cross-Service Contract Tests**: Validate Backend ↔ AI API contracts

---

## Contact

For issues or questions regarding constraint validation testing:

- Check existing documentation in `docs/DOCUMENT_CONSTRAINTS_SPECIFICATION.md`
- Review implementation guide in `docs/DOCUMENT_CONSTRAINTS_IMPLEMENTATION_GUIDE.md`
