# Document Constraints Specification

## BA Copilot - Document Dependency & Constraint System

**Version:** 1.0  
**Date:** December 31, 2024  
**Authors:** BA Copilot Team  
**Status:** Active

---

## 1. Executive Summary

This document defines the **Document Constraint System** for BA Copilot, which ensures that AI-generated artifacts are produced in a logical, dependency-aware sequence following industry-standard Software Development Life Cycle (SDLC) practices.

### 1.1 Purpose

- Enforce document generation order based on SDLC best practices
- Ensure prerequisite documents exist before generating dependent documents
- Improve AI output quality by providing relevant context from prerequisite documents
- Guide users through proper BA documentation workflow

### 1.2 Scope

This specification covers all 26 document types defined in the BA Copilot AI API:

| Phase                       | Document Types                                                              |
| --------------------------- | --------------------------------------------------------------------------- |
| Phase 1: Project Initiation | stakeholder-register, high-level-requirements, requirements-management-plan |
| Phase 2: Business Planning  | business-case, scope-statement, product-roadmap                             |
| Phase 3: Feasibility & Risk | feasibility-study, cost-benefit-analysis, risk-register, compliance         |
| Phase 4: High-Level Design  | hld-arch, hld-cloud, hld-tech                                               |
| Phase 5: Low-Level Design   | lld-arch, lld-db, lld-api, lld-pseudo                                       |
| Phase 6: UI/UX Design       | uiux-wireframe, uiux-mockup, uiux-prototype                                 |
| Phase 7: Testing & QA       | rtm                                                                         |
| Additional                  | srs, class-diagram, usecase-diagram, activity-diagram, wireframe            |

---

## 2. Industry Standards & Rationale

### 2.1 Standards Referenced

| Standard          | Description                          | Application                                  |
| ----------------- | ------------------------------------ | -------------------------------------------- |
| **BABOK v3**      | Business Analysis Body of Knowledge  | Requirements lifecycle, stakeholder analysis |
| **PMBOK 7th Ed**  | Project Management Body of Knowledge | Project planning, scope management           |
| **IEEE 830**      | Software Requirements Specification  | SRS structure and dependencies               |
| **ISO/IEC 25010** | Systems and software quality models  | Quality requirements                         |
| **TOGAF 10**      | Enterprise Architecture Framework    | Architecture documentation sequence          |
| **SAFe 6.0**      | Scaled Agile Framework               | Roadmap and planning artifacts               |

### 2.2 Rationale for Dependencies

#### 2.2.1 Information Flow Principle

Documents should be generated in an order that ensures:

1. **Upstream Context**: Later documents can reference earlier ones
2. **Decision Traceability**: Design decisions trace back to requirements
3. **Completeness**: All necessary inputs exist before generation
4. **Quality**: AI has sufficient context for accurate generation

#### 2.2.2 SDLC Phase Alignment

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        BA COPILOT SDLC FLOW                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  INITIATION ──▶ PLANNING ──▶ ANALYSIS ──▶ DESIGN ──▶ IMPLEMENTATION    │
│                                                                         │
│  ┌─────────┐   ┌──────────┐   ┌─────────┐   ┌──────────┐              │
│  │Stakehld │   │ Business │   │Feasibil.│   │HLD/LLD   │              │
│  │Register │──▶│ Case     │──▶│ Study   │──▶│Arch Docs │              │
│  │High-Lvl │   │ Scope    │   │ CBA     │   │UI/UX     │              │
│  │Reqs     │   │ Roadmap  │   │ Risks   │   │Designs   │              │
│  └─────────┘   └──────────┘   └─────────┘   └──────────┘              │
│       │              │              │              │                   │
│       └──────────────┴──────────────┴──────────────┘                   │
│                              │                                          │
│                              ▼                                          │
│                    ┌──────────────────┐                                │
│                    │ SRS (Synthesis)  │                                │
│                    │ RTM (Tracing)    │                                │
│                    └──────────────────┘                                │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Document Dependency Matrix

### 3.1 Dependency Definitions

| Dependency Type | Symbol | Description                                                               |
| --------------- | ------ | ------------------------------------------------------------------------- |
| **REQUIRED**    | 🔴     | Must exist before generation (hard block)                                 |
| **RECOMMENDED** | 🟡     | Should exist for better quality (user informed, can upload/generate/skip) |

### 3.2 Complete Dependency Matrix

#### Phase 1: Project Initiation

| Document                       | Required Prerequisites | Recommended                                   |
| ------------------------------ | ---------------------- | --------------------------------------------- |
| `stakeholder-register`         | _None (Entry Point)_   | -                                             |
| `high-level-requirements`      | _None (Entry Point)_   | stakeholder-register                          |
| `requirements-management-plan` | _None (Entry Point)_   | stakeholder-register, high-level-requirements |

#### Phase 2: Business Planning

| Document          | Required Prerequisites  | Recommended                              |
| ----------------- | ----------------------- | ---------------------------------------- |
| `business-case`   | stakeholder-register    | high-level-requirements, scope-statement |
| `scope-statement` | high-level-requirements | stakeholder-register, business-case      |
| `product-roadmap` | scope-statement         | business-case, high-level-requirements   |

#### Phase 3: Feasibility & Risk Analysis

| Document                | Required Prerequisites         | Recommended                             |
| ----------------------- | ------------------------------ | --------------------------------------- |
| `feasibility-study`     | business-case, scope-statement | high-level-requirements                 |
| `cost-benefit-analysis` | business-case                  | feasibility-study, scope-statement      |
| `risk-register`         | scope-statement                | feasibility-study, stakeholder-register |
| `compliance`            | scope-statement                | risk-register, high-level-requirements  |

#### Phase 4: High-Level Design

| Document    | Required Prerequisites                   | Recommended                              |
| ----------- | ---------------------------------------- | ---------------------------------------- |
| `hld-arch`  | high-level-requirements, scope-statement | feasibility-study                        |
| `hld-cloud` | hld-arch                                 | feasibility-study, cost-benefit-analysis |
| `hld-tech`  | hld-arch                                 | cost-benefit-analysis                    |

#### Phase 5: Low-Level Design

| Document     | Required Prerequisites            | Recommended      |
| ------------ | --------------------------------- | ---------------- |
| `lld-arch`   | hld-arch                          | hld-tech         |
| `lld-db`     | hld-arch, high-level-requirements | lld-arch         |
| `lld-api`    | hld-arch, high-level-requirements | lld-arch, lld-db |
| `lld-pseudo` | lld-arch                          | lld-api          |

#### Phase 6: UI/UX Design

| Document         | Required Prerequisites  | Recommended                           |
| ---------------- | ----------------------- | ------------------------------------- |
| `uiux-wireframe` | high-level-requirements | scope-statement, stakeholder-register |
| `uiux-mockup`    | uiux-wireframe          | hld-arch                              |
| `uiux-prototype` | uiux-mockup             | uiux-wireframe, lld-api               |

#### Phase 7: Testing & QA

| Document | Required Prerequisites       | Recommended                      |
| -------- | ---------------------------- | -------------------------------- |
| `rtm`    | high-level-requirements, srs | scope-statement, all design docs |

#### Synthesis Documents

| Document | Required Prerequisites                   | Recommended                                             |
| -------- | ---------------------------------------- | ------------------------------------------------------- |
| `srs`    | high-level-requirements, scope-statement | stakeholder-register, business-case, all Phase 1-3 docs |

#### Diagram Documents

| Document           | Required Prerequisites  | Recommended                      |
| ------------------ | ----------------------- | -------------------------------- |
| `class-diagram`    | high-level-requirements | lld-arch, lld-db, srs            |
| `usecase-diagram`  | high-level-requirements | stakeholder-register, srs        |
| `activity-diagram` | high-level-requirements | scope-statement, usecase-diagram |
| `wireframe`        | high-level-requirements | uiux-wireframe, scope-statement  |

---

## 4. Constraint Enforcement Levels

### 4.1 Enforcement Modes

The system supports three enforcement modes:

| Mode           | Behavior                                  | Use Case                     |
| -------------- | ----------------------------------------- | ---------------------------- |
| **STRICT**     | Block generation if REQUIRED deps missing | Production, quality-critical |
| **GUIDED**     | Warn but allow override for REQUIRED deps | Development, learning        |
| **PERMISSIVE** | Log only, no blocking                     | Demo, testing                |

**Default Mode:** `GUIDED`

### 4.2 User Actions on Constraint Violation

When a constraint is violated, users can:

1. **Generate Prerequisites First** - System suggests which documents to create
2. **Upload Existing Documents** - User uploads their own documents matching the type
3. **Override with Justification** - In GUIDED mode, user can proceed with explanation
4. **Skip (Admin Only)** - Bypass constraint checking entirely

---

## 5. Metadata-Based Detection

### 5.1 How Documents Are Identified

The system identifies existing documents by checking the `metadata` JSONB field in the `files` table:

```sql
-- Schema: files.metadata structure
{
  "document_types": [
    {
      "type": "stakeholder-register",
      "line_start": 1,
      "line_end": 150
    },
    {
      "type": "high-level-requirements",
      "line_start": 152,
      "line_end": 300
    }
  ],
  "extraction_timestamp": "2024-12-31T10:00:00Z",
  "file_category": "ai_generated" | "uploaded",
  "file_type": "stakeholder-register",
  "source": "ai_generated" | "metadata_extraction"
}
```

**Note:** User manual tagging during upload is considered for future implementation but the current system does not depend on it.

### 5.2 Document Sources

| Source                     | Detection Method             | Metadata Field                                             |
| -------------------------- | ---------------------------- | ---------------------------------------------------------- |
| **AI Generated**           | Created by AI endpoints      | `file_category: "ai generated"`, `file_type: "<doc-type>"` |
| **User Upload (Detected)** | Metadata extraction workflow | `metadata.document_types[]`                                |

**Note:** Manual user tagging during upload is planned for future implementation but is not currently depended upon for constraint checking.

### 5.3 Metadata Extraction Integration

When a user uploads a file:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    UPLOAD + METADATA EXTRACTION FLOW                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  User Upload ──▶ Convert to MD ──▶ Call AI Metadata Extraction         │
│       │                                    │                            │
│       │                                    ▼                            │
│       │                          ┌─────────────────┐                   │
│       │                          │ Detected Types: │                   │
│       │                          │ - stakeholder   │                   │
│       │                          │ - requirements  │                   │
│       │                          └─────────────────┘                   │
│       │                                    │                            │
│       ▼                                    ▼                            │
│  Save File ◀──────────────────── Update Metadata                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 6. System Architecture Flow

### 6.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CONSTRAINT ENFORCEMENT ARCHITECTURE                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────┐     ┌──────────────┐     ┌──────────────┐     ┌───────────┐  │
│  │ FRONTEND │────▶│   BACKEND    │────▶│  CONSTRAINT  │────▶│    AI     │  │
│  │          │     │   Gateway    │     │   SERVICE    │     │  SERVICE  │  │
│  └──────────┘     └──────────────┘     └──────────────┘     └───────────┘  │
│       │                  │                    │                    │        │
│       │                  │                    │                    │        │
│       ▼                  ▼                    ▼                    ▼        │
│  ┌──────────┐     ┌──────────────┐     ┌──────────────┐     ┌───────────┐  │
│  │ Display  │     │   Validate   │     │    Check     │     │  Enhanced │  │
│  │ Warnings │◀────│   Request    │◀────│ Prerequisites│     │  Prompts  │  │
│  │ & Block  │     │   + Auth     │     │   in DB      │     │ w/Context │  │
│  └──────────┘     └──────────────┘     └──────────────┘     └───────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Request Processing Flow

#### 6.2.1 Happy Path (All Prerequisites Met)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              HAPPY PATH FLOW                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. Frontend Request                                                         │
│     POST /api/v1/design/generate                                            │
│     {doc_type: "uiux-wireframe", message: "Create login page..."}          │
│                                    │                                         │
│                                    ▼                                         │
│  2. Backend Receives Request                                                │
│     ├── Authenticate user (JWT)                                             │
│     ├── Validate doc_type                                                   │
│     └── Call ConstraintService.check_prerequisites()                        │
│                                    │                                         │
│                                    ▼                                         │
│  3. Constraint Service Checks                                               │
│     ├── Query files table for project_id                                    │
│     ├── Extract document types from metadata                                │
│     ├── Compare against REQUIRED for "uiux-wireframe"                       │
│     │   └── Required: ["high-level-requirements"] ✅ FOUND                  │
│     └── Return: {satisfied: true, missing: [], available_context: [...]}   │
│                                    │                                         │
│                                    ▼                                         │
│  4. Backend Calls AI Service                                                │
│     POST http://ai:8000/api/v1/generate/uiux-wireframe                     │
│     {                                                                        │
│       message: "Create login page...",                                      │
│       storage_paths: ["/2/1/high-level-requirements.md", ...],             │
│       content_id: null,                                                     │
│       constraint_context: {                                                 │
│         available_docs: ["high-level-requirements", "stakeholder-register"],│
│         doc_type: "uiux-wireframe"                                         │
│       }                                                                      │
│     }                                                                        │
│                                    │                                         │
│                                    ▼                                         │
│  5. AI Generates with Enhanced Context                                      │
│     ├── Load prerequisite documents from storage_paths                      │
│     ├── Use constraint-aware prompt template                                │
│     └── Generate wireframe referencing requirements                         │
│                                    │                                         │
│                                    ▼                                         │
│  6. Backend Saves & Returns                                                 │
│     ├── Save to Supabase storage                                            │
│     ├── Create files record with metadata                                   │
│     └── Return success response to frontend                                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 6.2.2 Error Path: Missing Required Prerequisites

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ERROR PATH: MISSING PREREQUISITES                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. Frontend Request                                                         │
│     POST /api/v1/design/generate                                            │
│     {doc_type: "uiux-mockup", message: "Create dashboard mockup..."}       │
│                                    │                                         │
│                                    ▼                                         │
│  2. Backend Constraint Check                                                │
│     ConstraintService.check_prerequisites("uiux-mockup", project_id)        │
│     │                                                                        │
│     ├── Required: ["uiux-wireframe"] ❌ NOT FOUND                           │
│     └── Return: {                                                           │
│           satisfied: false,                                                  │
│           missing_required: ["uiux-wireframe"],                             │
│           missing_recommended: ["hld-arch"],                                │
│           suggestions: [                                                     │
│             {action: "generate", doc_type: "uiux-wireframe"},               │
│             {action: "upload", doc_type: "uiux-wireframe"}                  │
│           ]                                                                  │
│         }                                                                    │
│                                    │                                         │
│                                    ▼                                         │
│  3. Backend Returns 422 Unprocessable Entity                                │
│     {                                                                        │
│       "error": "PREREQUISITE_MISSING",                                      │
│       "message": "Cannot generate uiux-mockup without prerequisites",       │
│       "details": {                                                          │
│         "doc_type": "uiux-mockup",                                          │
│         "missing_required": ["uiux-wireframe"],                             │
│         "missing_recommended": ["hld-arch"],                                │
│         "suggestions": [...]                                                 │
│       }                                                                      │
│     }                                                                        │
│                                    │                                         │
│                                    ▼                                         │
│  4. Frontend Displays Constraint Error                                      │
│     ┌─────────────────────────────────────────────┐                         │
│     │ ⚠️ Prerequisites Required                    │                         │
│     │                                              │                         │
│     │ To generate "UI/UX Mockup", you need:       │                         │
│     │                                              │                         │
│     │ 🔴 Required (Missing):                       │                         │
│     │    • UI/UX Wireframe                        │                         │
│     │                                              │                         │
│     │ 🟡 Recommended (Missing):                    │                         │
│     │    • System Architecture (HLD)              │                         │
│     │                                              │                         │
│     │ [Generate Wireframe] [Upload Document]      │                         │
│     └─────────────────────────────────────────────┘                         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.3 WebSocket Orchestration Flow

For multi-document generation via WebSocket:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     WEBSOCKET CONSTRAINT FLOW                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Client ──ws://──▶ Backend WebSocket Handler                                │
│                                                                              │
│  1. Client sends "generate" action:                                         │
│     {                                                                        │
│       action: "generate",                                                   │
│       steps: [                                                              │
│         {doc_types: ["stakeholder-register", "high-level-requirements"]},  │
│         {doc_types: ["business-case", "scope-statement"]},                 │
│         {doc_types: ["uiux-wireframe"]}                                    │
│       ]                                                                      │
│     }                                                                        │
│                                    │                                         │
│                                    ▼                                         │
│  2. Backend validates ALL steps upfront                                     │
│     for each step:                                                          │
│       for each doc_type in step:                                            │
│         check_prerequisites(doc_type, project_id, generated_so_far)         │
│                                    │                                         │
│                                    ▼                                         │
│  3a. If validation fails for ANY step:                                      │
│      Send error before starting:                                            │
│      {                                                                       │
│        type: "validation_error",                                            │
│        step: 2,                                                             │
│        doc_type: "business-case",                                           │
│        missing: ["stakeholder-register"],                                   │
│        message: "Step 2 requires stakeholder-register from Step 1"         │
│      }                                                                       │
│                                    │                                         │
│                                    ▼                                         │
│  3b. If validation passes:                                                  │
│      Begin sequential generation with real-time updates                     │
│                                                                              │
│  4. As each document completes:                                             │
│     ├── Update generated_so_far list                                        │
│     ├── Re-validate next document's prerequisites                           │
│     └── Send doc_completed message                                          │
│                                                                              │
│  5. Between steps: send await_decision                                      │
│     User can review and continue or stop                                    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Constraint Data Structures

### 7.1 Constraint Definition Schema

```python
@dataclass
class DocumentConstraint:
    """Constraint definition for a document type."""
    doc_type: str
    display_name: str
    phase: int
    required: List[str]          # Must exist (hard block)
    recommended: List[str]       # Should exist (informational)
    description: str
    generation_endpoint: str
```

### 7.2 Constraint Check Result Schema

```python
@dataclass
class ConstraintCheckResult:
    """Result of checking prerequisites for a document type."""
    doc_type: str
    satisfied: bool
    enforcement_mode: str         # "STRICT" | "GUIDED" | "PERMISSIVE"

    # Missing prerequisites
    missing_required: List[str]
    missing_recommended: List[str]

    # Available context to pass to AI
    available_docs: List[str]
    available_storage_paths: List[str]

    # User guidance
    suggestions: List[Dict]       # Actions user can take
    error_message: Optional[str]
    warning_message: Optional[str]
```

### 7.3 API Error Response Schema

```json
{
  "error": "PREREQUISITE_MISSING",
  "message": "Cannot generate {doc_type} without required prerequisites",
  "details": {
    "doc_type": "string",
    "enforcement_mode": "STRICT | GUIDED | PERMISSIVE",
    "missing_required": ["string"],
    "missing_recommended": ["string"],
    "available_docs": ["string"],
    "suggestions": [
      {
        "action": "generate | upload | override",
        "doc_type": "string",
        "endpoint": "string",
        "display_name": "string"
      }
    ]
  }
}
```

---

## 8. User Experience Guidelines

### 8.1 Error Message Templates

#### Missing Required Prerequisite

```
❌ Cannot Generate {Display Name}

Required documents are missing:
• {Missing Doc 1 Display Name}
• {Missing Doc 2 Display Name}

To proceed, you can:
1. Generate the required documents first
2. Upload existing documents of these types
```

#### Missing Recommended Prerequisite

```
⚠️ Generating {Display Name} with Limited Context

Recommended documents are missing:
• {Missing Doc 1 Display Name}

The output quality may be improved by:
1. Generating these documents first
2. Uploading existing documents

[Continue Anyway] [Generate Prerequisites]
```

### 8.2 Dependency Graph Visibility

**Current Approach:** The complete dependency graph is hidden from users to reduce complexity. Users only see:

- Missing required prerequisites (blocking)
- Missing recommended prerequisites (informational)
- Suggested actions (generate, upload, skip)

**Future Consideration:** Interactive dependency visualization may be added later.

---

## 9. Configuration Options

### 9.1 Environment Variables

```bash
# Constraint enforcement mode
CONSTRAINT_ENFORCEMENT_MODE=GUIDED  # STRICT | GUIDED | PERMISSIVE

# Enable/disable AI context validation
AI_CONTEXT_VALIDATION_ENABLED=true

# Minimum content length for prerequisite to be considered valid
MIN_PREREQUISITE_CONTENT_LENGTH=100

# Allow admin override of constraints
ALLOW_CONSTRAINT_OVERRIDE=true
```

### 9.2 Per-Project Settings

```json
{
  "constraint_settings": {
    "enforcement_mode": "STRICT",
    "allow_override": false,
    "skip_recommended_warnings": false
  }
}
```

---

## 10. Future Considerations

### 10.1 Planned Enhancements

1. **Circular Dependency Detection**: Prevent constraint loops
2. **Version Compatibility**: Track document versions for updates
3. **Custom Constraints**: Allow project-specific constraint rules
4. **Dependency Visualization**: Interactive dependency graph UI
5. **Auto-Generation Chains**: Automatically generate full prerequisite chains

### 10.2 Integration Points

- **CI/CD Pipelines**: Constraint validation in automated workflows
- **Template Library**: Pre-defined constraint sets for common project types
- **Analytics Dashboard**: Track constraint violations and user patterns

---

## 11. API Specification

### 11.1 Happy Path: All Prerequisites Satisfied

#### Request

```http
POST /api/v1/design/generate
Authorization: Bearer {jwt_token}
Content-Type: multipart/form-data

doc_type: uiux-wireframe
message: Create wireframes for a mobile banking app with account overview, transfer funds, and transaction history screens
project_id: 550e8400-e29b-41d4-a716-446655440000
```

#### Backend Processing

```python
# 1. Extract parameters
doc_type = "uiux-wireframe"
project_id = "550e8400-e29b-41d4-a716-446655440000"

# 2. Check constraints
constraint = get_constraint(doc_type)
# Returns: DocumentConstraint(
#   required=["high-level-requirements"],
#   recommended=["scope-statement", "stakeholder-register"]
# )

# 3. Query database for existing documents
existing_docs = db.query(Files).filter(
    Files.project_id == project_id,
    Files.metadata["document_types"].contains(["high-level-requirements"])
).all()

# 4. Check result
# Found: high-level-requirements (id=123)
# Found: stakeholder-register (id=124)
# Missing recommended: scope-statement

available_docs = ["high-level-requirements", "stakeholder-register"]
available_paths = ["project_550e/requirements.md", "project_550e/stakeholders.md"]
missing_recommended = ["scope-statement"]

# 5. Constraint satisfied (all REQUIRED met)
result = ConstraintCheckResult(
    satisfied=True,
    missing_required=[],
    missing_recommended=["scope-statement"],
    available_docs=available_docs,
    available_storage_paths=available_paths
)

# 6. Forward to AI service with context
ai_request = {
    "doc_type": "uiux-wireframe",
    "message": "Create wireframes...",
    "project_id": project_id,
    "available_docs": available_docs,
    "available_storage_paths": available_paths
}
```

#### AI Service Processing

```python
# AI receives request and loads prerequisite documents
prerequisite_content = ""
for path in available_storage_paths:
    content = storage.download(path)
    prerequisite_content += f"\n\n=== {path} ===\n{content}"

# Generate with context
final_prompt = f"""
PREREQUISITE DOCUMENTS:
{prerequisite_content}

USER REQUEST:
Create wireframes for a mobile banking app...

Based on the requirements above, create comprehensive wireframe specifications...
"""

# Generate and return
```

#### Response (Success)

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "success",
  "message": "UI/UX Wireframe generated successfully",
  "data": {
    "file_id": "660e8400-e29b-41d4-a716-446655440111",
    "file_name": "uiux-wireframe-20250102.md",
    "storage_path": "project_550e/uiux-wireframe-20250102.md",
    "doc_type": "uiux-wireframe",
    "created_at": "2025-01-02T10:30:00Z"
  },
  "warnings": {
    "missing_recommended": ["scope-statement"],
    "suggestion": "Consider generating or uploading 'Scope Statement' to improve output quality"
  }
}
```

---

### 11.2 Error Path: Missing Required Prerequisites

#### Request

```http
POST /api/v1/design/generate
Authorization: Bearer {jwt_token}
Content-Type: multipart/form-data

doc_type: uiux-mockup
message: Create high-fidelity mockup for the dashboard with modern design
project_id: 550e8400-e29b-41d4-a716-446655440000
```

#### Backend Processing

```python
# 1. Extract parameters
doc_type = "uiux-mockup"
project_id = "550e8400-e29b-41d4-a716-446655440000"

# 2. Check constraints
constraint = get_constraint(doc_type)
# Returns: DocumentConstraint(
#   required=["uiux-wireframe"],
#   recommended=["hld-arch"]
# )

# 3. Query database for existing documents
existing_docs = db.query(Files).filter(
    Files.project_id == project_id,
    Files.metadata["document_types"].contains(["uiux-wireframe"])
).all()

# 4. Check result
# NOT FOUND: uiux-wireframe ❌
# NOT FOUND: hld-arch

missing_required = ["uiux-wireframe"]
missing_recommended = ["hld-arch"]

# 5. Constraint NOT satisfied
result = ConstraintCheckResult(
    satisfied=False,
    missing_required=["uiux-wireframe"],
    missing_recommended=["hld-arch"],
    available_docs=[],
    available_storage_paths=[]
)

# 6. Build suggestions
suggestions = [
    {
        "action": "generate",
        "doc_type": "uiux-wireframe",
        "display_name": "UI/UX Wireframe",
        "endpoint": "/api/v1/design/generate",
        "description": "Generate the wireframe first to establish layout structure"
    },
    {
        "action": "upload",
        "doc_type": "uiux-wireframe",
        "display_name": "UI/UX Wireframe",
        "description": "Upload an existing wireframe document"
    }
]

# 7. Return error (do NOT call AI service)
```

#### Response (Error - 422 Unprocessable Entity)

```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json

{
  "error": "PREREQUISITE_MISSING",
  "message": "Cannot generate UI/UX Mockup without required prerequisites",
  "details": {
    "doc_type": "uiux-mockup",
    "display_name": "UI/UX Mockup",
    "enforcement_mode": "GUIDED",
    "missing_required": [
      {
        "doc_type": "uiux-wireframe",
        "display_name": "UI/UX Wireframe"
      }
    ],
    "missing_recommended": [
      {
        "doc_type": "hld-arch",
        "display_name": "High-Level Architecture"
      }
    ],
    "available_docs": [],
    "suggestions": [
      {
        "action": "generate",
        "doc_type": "uiux-wireframe",
        "display_name": "UI/UX Wireframe",
        "endpoint": "/api/v1/design/generate",
        "description": "Generate the wireframe first to establish layout structure"
      },
      {
        "action": "upload",
        "doc_type": "uiux-wireframe",
        "display_name": "UI/UX Wireframe",
        "description": "Upload an existing wireframe document"
      }
    ]
  }
}
```

#### Frontend Display

```
┌─────────────────────────────────────────────┐
│ ⚠️ Prerequisites Required                    │
│                                              │
│ To generate "UI/UX Mockup", you need:       │
│                                              │
│ 🔴 Required (Missing):                       │
│    • UI/UX Wireframe                        │
│                                              │
│ 🟡 Recommended (Missing):                    │
│    • High-Level Architecture                │
│                                              │
│ [Generate Wireframe] [Upload Document]      │
│ [Skip & Continue Anyway]                    │
└─────────────────────────────────────────────┘
```

---

### 11.3 WebSocket Multi-Document Generation

#### Request (Step-by-Step Validation)

```json
{
  "action": "generate",
  "steps": [
    {
      "step_number": 1,
      "doc_types": ["stakeholder-register", "high-level-requirements"],
      "messages": {
        "stakeholder-register": "Create stakeholder register for hospital management system",
        "high-level-requirements": "Define requirements for patient records, appointments, billing"
      }
    },
    {
      "step_number": 2,
      "doc_types": ["business-case", "scope-statement"],
      "messages": {
        "business-case": "Business justification for the HMS",
        "scope-statement": "Define scope boundaries"
      }
    }
  ],
  "project_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### Backend Validation (Before Starting)

```python
# Validate ALL steps upfront
generated_so_far = []

for step in steps:
    for doc_type in step.doc_types:
        result = check_prerequisites(
            doc_type,
            project_id,
            existing_docs + generated_so_far
        )

        if not result.satisfied:
            # Send error and STOP
            ws.send({
                "type": "validation_error",
                "step": step.step_number,
                "doc_type": doc_type,
                "missing_required": result.missing_required,
                "message": f"Step {step.step_number} cannot proceed..."
            })
            return

# All validated ✓ - proceed with generation
```

#### WebSocket Messages (Progressive Updates)

```json
// Step 1 Start
{"type": "step_start", "step": 1, "total_steps": 2}

// Document 1
{"type": "doc_start", "doc_type": "stakeholder-register", "display_name": "Stakeholder Register"}
{"type": "doc_progress", "doc_type": "stakeholder-register", "progress": 50}
{"type": "doc_completed", "doc_type": "stakeholder-register", "file_id": "abc-123", "storage_path": "project_550e/stakeholder-register.md"}

// Document 2
{"type": "doc_start", "doc_type": "high-level-requirements"}
{"type": "doc_progress", "doc_type": "high-level-requirements", "progress": 75}
{"type": "doc_completed", "doc_type": "high-level-requirements", "file_id": "abc-124"}

// Step completed
{"type": "step_completed", "step": 1}
{"type": "await_decision", "message": "Step 1 complete. Review documents before continuing to Step 2"}

// User continues...

// Step 2 Start
{"type": "step_start", "step": 2}
// ... (similar pattern)
```

---

## Appendix A: Complete Constraint Mapping

```python
DOCUMENT_CONSTRAINTS = {
    # Phase 1: Project Initiation (Entry Points)
    "stakeholder-register": {
        "required": [],
        "recommended": []
    },
    "high-level-requirements": {
        "required": [],
        "recommended": ["stakeholder-register"]
    },
    "requirements-management-plan": {
        "required": [],
        "recommended": ["stakeholder-register", "high-level-requirements"]
    },

    # Phase 2: Business Planning
    "business-case": {
        "required": ["stakeholder-register"],
        "recommended": ["high-level-requirements", "scope-statement"]
    },
    "scope-statement": {
        "required": ["high-level-requirements"],
        "recommended": ["stakeholder-register", "business-case"]
    },
    "product-roadmap": {
        "required": ["scope-statement"],
        "recommended": ["business-case", "high-level-requirements"]
    },

    # Phase 3: Feasibility & Risk
    "feasibility-study": {
        "required": ["business-case", "scope-statement"],
        "recommended": ["high-level-requirements"]
    },
    "cost-benefit-analysis": {
        "required": ["business-case"],
        "recommended": ["feasibility-study", "scope-statement"]
    },
    "risk-register": {
        "required": ["scope-statement"],
        "recommended": ["feasibility-study", "stakeholder-register"]
    },
    "compliance": {
        "required": ["scope-statement"],
        "recommended": ["risk-register", "high-level-requirements"]
    },

    # Phase 4: High-Level Design
    "hld-arch": {
        "required": ["high-level-requirements", "scope-statement"],
        "recommended": ["feasibility-study"]
    },
    "hld-cloud": {
        "required": ["hld-arch"],
        "recommended": ["feasibility-study", "cost-benefit-analysis"]
    },
    "hld-tech": {
        "required": ["hld-arch"],
        "recommended": ["cost-benefit-analysis"]
    },

    # Phase 5: Low-Level Design
    "lld-arch": {
        "required": ["hld-arch"],
        "recommended": ["hld-tech"]
    },
    "lld-db": {
        "required": ["hld-arch", "high-level-requirements"],
        "recommended": ["lld-arch"]
    },
    "lld-api": {
        "required": ["hld-arch", "high-level-requirements"],
        "recommended": ["lld-arch", "lld-db"]
    },
    "lld-pseudo": {
        "required": ["lld-arch"],
        "recommended": ["lld-api"]
    },

    # Phase 6: UI/UX Design
    "uiux-wireframe": {
        "required": ["high-level-requirements"],
        "recommended": ["scope-statement", "stakeholder-register"]
    },
    "uiux-mockup": {
        "required": ["uiux-wireframe"],
        "recommended": ["hld-arch"]
    },
    "uiux-prototype": {
        "required": ["uiux-mockup"],
        "recommended": ["uiux-wireframe", "lld-api"]
    },

    # Phase 7: Testing
    "rtm": {
        "required": ["high-level-requirements", "srs"],
        "recommended": ["scope-statement"]
    },

    # Synthesis
    "srs": {
        "required": ["high-level-requirements", "scope-statement"],
        "recommended": ["stakeholder-register", "business-case"]
    },

    # Diagrams
    "class-diagram": {
        "required": ["high-level-requirements"],
        "recommended": ["lld-arch", "lld-db", "srs"]
    },
    "usecase-diagram": {
        "required": ["high-level-requirements"],
        "recommended": ["stakeholder-register", "srs"]
    },
    "activity-diagram": {
        "required": ["high-level-requirements"],
        "recommended": ["scope-statement", "usecase-diagram"]
    },
    "wireframe": {
        "required": ["high-level-requirements"],
        "recommended": ["uiux-wireframe", "scope-statement"]
    }
}
```

---

**Document End**
