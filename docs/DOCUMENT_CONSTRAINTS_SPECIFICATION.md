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

| Dependency Type | Symbol | Description                                    |
| --------------- | ------ | ---------------------------------------------- |
| **REQUIRED**    | 🔴     | Must exist before generation (hard block)      |
| **RECOMMENDED** | 🟡     | Should exist for better quality (soft warning) |
| **ENHANCES**    | 🟢     | Improves output if available (no warning)      |

### 3.2 Complete Dependency Matrix

#### Phase 1: Project Initiation

| Document                       | Required Prerequisites | Recommended                                   | Enhances     |
| ------------------------------ | ---------------------- | --------------------------------------------- | ------------ |
| `stakeholder-register`         | _None (Entry Point)_   | User uploads                                  | -            |
| `high-level-requirements`      | _None (Entry Point)_   | stakeholder-register                          | User uploads |
| `requirements-management-plan` | _None (Entry Point)_   | stakeholder-register, high-level-requirements | -            |

#### Phase 2: Business Planning

| Document          | Required Prerequisites  | Recommended                            | Enhances        |
| ----------------- | ----------------------- | -------------------------------------- | --------------- |
| `business-case`   | stakeholder-register    | high-level-requirements                | scope-statement |
| `scope-statement` | high-level-requirements | stakeholder-register, business-case    | -               |
| `product-roadmap` | scope-statement         | business-case, high-level-requirements | -               |

#### Phase 3: Feasibility & Risk Analysis

| Document                | Required Prerequisites         | Recommended                             | Enhances |
| ----------------------- | ------------------------------ | --------------------------------------- | -------- |
| `feasibility-study`     | business-case, scope-statement | high-level-requirements                 | -        |
| `cost-benefit-analysis` | business-case                  | feasibility-study, scope-statement      | -        |
| `risk-register`         | scope-statement                | feasibility-study, stakeholder-register | -        |
| `compliance`            | scope-statement                | risk-register, high-level-requirements  | -        |

#### Phase 4: High-Level Design

| Document    | Required Prerequisites                   | Recommended                              | Enhances |
| ----------- | ---------------------------------------- | ---------------------------------------- | -------- |
| `hld-arch`  | high-level-requirements, scope-statement | feasibility-study                        | -        |
| `hld-cloud` | hld-arch                                 | feasibility-study, cost-benefit-analysis | -        |
| `hld-tech`  | hld-arch                                 | cost-benefit-analysis                    | -        |

#### Phase 5: Low-Level Design

| Document     | Required Prerequisites            | Recommended      | Enhances |
| ------------ | --------------------------------- | ---------------- | -------- |
| `lld-arch`   | hld-arch                          | hld-tech         | -        |
| `lld-db`     | hld-arch, high-level-requirements | lld-arch         | -        |
| `lld-api`    | hld-arch, high-level-requirements | lld-arch, lld-db | -        |
| `lld-pseudo` | lld-arch                          | lld-api          | -        |

#### Phase 6: UI/UX Design

| Document         | Required Prerequisites  | Recommended                           | Enhances |
| ---------------- | ----------------------- | ------------------------------------- | -------- |
| `uiux-wireframe` | high-level-requirements | scope-statement, stakeholder-register | -        |
| `uiux-mockup`    | uiux-wireframe          | hld-arch                              | -        |
| `uiux-prototype` | uiux-mockup             | uiux-wireframe, lld-api               | -        |

#### Phase 7: Testing & QA

| Document | Required Prerequisites       | Recommended     | Enhances        |
| -------- | ---------------------------- | --------------- | --------------- |
| `rtm`    | high-level-requirements, srs | scope-statement | All design docs |

#### Synthesis Documents

| Document | Required Prerequisites                   | Recommended                         | Enhances           |
| -------- | ---------------------------------------- | ----------------------------------- | ------------------ |
| `srs`    | high-level-requirements, scope-statement | stakeholder-register, business-case | All Phase 1-3 docs |

#### Diagram Documents

| Document           | Required Prerequisites  | Recommended          | Enhances        |
| ------------------ | ----------------------- | -------------------- | --------------- |
| `class-diagram`    | high-level-requirements | lld-arch, lld-db     | srs             |
| `usecase-diagram`  | high-level-requirements | stakeholder-register | srs             |
| `activity-diagram` | high-level-requirements | scope-statement      | usecase-diagram |
| `wireframe`        | high-level-requirements | uiux-wireframe       | scope-statement |

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
  "source": "ai_generated" | "user_upload" | "metadata_extraction"
}
```

### 5.2 Document Sources

| Source                     | Detection Method             | Metadata Field                                             |
| -------------------------- | ---------------------------- | ---------------------------------------------------------- |
| **AI Generated**           | Created by AI endpoints      | `file_category: "ai generated"`, `file_type: "<doc-type>"` |
| **User Upload (Detected)** | Metadata extraction workflow | `metadata.document_types[]`                                |
| **User Upload (Manual)**   | User tags during upload      | `metadata.manual_tags[]`                                   |

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

#### 6.2.3 Error Path: AI Detects Insufficient Context

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ERROR PATH: AI CONTEXT VALIDATION                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  This path handles cases where:                                              │
│  - Prerequisites exist but are empty/minimal                                 │
│  - Document content doesn't match expected type                              │
│  - Context is insufficient for quality generation                            │
│                                    │                                         │
│                                    ▼                                         │
│  1. Backend passes constraint check (docs exist)                            │
│                                    │                                         │
│                                    ▼                                         │
│  2. AI Service Receives Request                                             │
│     ├── Load prerequisite documents                                         │
│     ├── Analyze content quality/relevance                                   │
│     └── Detect: high-level-requirements.md is nearly empty (< 100 chars)   │
│                                    │                                         │
│                                    ▼                                         │
│  3. AI Returns Warning Response                                             │
│     {                                                                        │
│       "type": "uiux-wireframe",                                             │
│       "response": {...},           // Generated content (best effort)       │
│       "warnings": [                                                         │
│         {                                                                    │
│           "code": "INSUFFICIENT_CONTEXT",                                   │
│           "message": "high-level-requirements document is minimal",         │
│           "suggestion": "Add more detail to requirements for better output" │
│         }                                                                    │
│       ],                                                                     │
│       "quality_score": 0.6         // Estimated output quality              │
│     }                                                                        │
│                                    │                                         │
│                                    ▼                                         │
│  4. Backend Forwards Warning to Frontend                                    │
│     HTTP 200 with warnings in response body                                 │
│     OR HTTP 207 Multi-Status if significant issues                          │
│                                    │                                         │
│                                    ▼                                         │
│  5. Frontend Displays Warning                                               │
│     ┌─────────────────────────────────────────────┐                         │
│     │ ⚠️ Document Generated with Warnings          │                         │
│     │                                              │                         │
│     │ The wireframe was generated but quality     │                         │
│     │ may be affected:                            │                         │
│     │                                              │                         │
│     │ • High-level requirements doc is minimal    │                         │
│     │                                              │                         │
│     │ [View Anyway] [Improve Requirements First]  │                         │
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
    recommended: List[str]       # Should exist (warning)
    enhances: List[str]          # Nice to have (no warning)
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

    # Available context for AI
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

### 8.2 Progressive Disclosure

1. **Simple View**: Show only critical missing prerequisites
2. **Detailed View**: Show full dependency tree on expand
3. **Expert View**: Show all constraints including ENHANCES level

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

## Appendix A: Complete Constraint Mapping

```python
DOCUMENT_CONSTRAINTS = {
    # Phase 1: Project Initiation (Entry Points)
    "stakeholder-register": {
        "required": [],
        "recommended": [],
        "enhances": []
    },
    "high-level-requirements": {
        "required": [],
        "recommended": ["stakeholder-register"],
        "enhances": []
    },
    "requirements-management-plan": {
        "required": [],
        "recommended": ["stakeholder-register", "high-level-requirements"],
        "enhances": []
    },

    # Phase 2: Business Planning
    "business-case": {
        "required": ["stakeholder-register"],
        "recommended": ["high-level-requirements"],
        "enhances": ["scope-statement"]
    },
    "scope-statement": {
        "required": ["high-level-requirements"],
        "recommended": ["stakeholder-register", "business-case"],
        "enhances": []
    },
    "product-roadmap": {
        "required": ["scope-statement"],
        "recommended": ["business-case", "high-level-requirements"],
        "enhances": []
    },

    # Phase 3: Feasibility & Risk
    "feasibility-study": {
        "required": ["business-case", "scope-statement"],
        "recommended": ["high-level-requirements"],
        "enhances": []
    },
    "cost-benefit-analysis": {
        "required": ["business-case"],
        "recommended": ["feasibility-study", "scope-statement"],
        "enhances": []
    },
    "risk-register": {
        "required": ["scope-statement"],
        "recommended": ["feasibility-study", "stakeholder-register"],
        "enhances": []
    },
    "compliance": {
        "required": ["scope-statement"],
        "recommended": ["risk-register", "high-level-requirements"],
        "enhances": []
    },

    # Phase 4: High-Level Design
    "hld-arch": {
        "required": ["high-level-requirements", "scope-statement"],
        "recommended": ["feasibility-study"],
        "enhances": []
    },
    "hld-cloud": {
        "required": ["hld-arch"],
        "recommended": ["feasibility-study", "cost-benefit-analysis"],
        "enhances": []
    },
    "hld-tech": {
        "required": ["hld-arch"],
        "recommended": ["cost-benefit-analysis"],
        "enhances": []
    },

    # Phase 5: Low-Level Design
    "lld-arch": {
        "required": ["hld-arch"],
        "recommended": ["hld-tech"],
        "enhances": []
    },
    "lld-db": {
        "required": ["hld-arch", "high-level-requirements"],
        "recommended": ["lld-arch"],
        "enhances": []
    },
    "lld-api": {
        "required": ["hld-arch", "high-level-requirements"],
        "recommended": ["lld-arch", "lld-db"],
        "enhances": []
    },
    "lld-pseudo": {
        "required": ["lld-arch"],
        "recommended": ["lld-api"],
        "enhances": []
    },

    # Phase 6: UI/UX Design
    "uiux-wireframe": {
        "required": ["high-level-requirements"],
        "recommended": ["scope-statement", "stakeholder-register"],
        "enhances": []
    },
    "uiux-mockup": {
        "required": ["uiux-wireframe"],
        "recommended": ["hld-arch"],
        "enhances": []
    },
    "uiux-prototype": {
        "required": ["uiux-mockup"],
        "recommended": ["uiux-wireframe", "lld-api"],
        "enhances": []
    },

    # Phase 7: Testing
    "rtm": {
        "required": ["high-level-requirements", "srs"],
        "recommended": ["scope-statement"],
        "enhances": []
    },

    # Synthesis
    "srs": {
        "required": ["high-level-requirements", "scope-statement"],
        "recommended": ["stakeholder-register", "business-case"],
        "enhances": []
    },

    # Diagrams
    "class-diagram": {
        "required": ["high-level-requirements"],
        "recommended": ["lld-arch", "lld-db"],
        "enhances": ["srs"]
    },
    "usecase-diagram": {
        "required": ["high-level-requirements"],
        "recommended": ["stakeholder-register"],
        "enhances": ["srs"]
    },
    "activity-diagram": {
        "required": ["high-level-requirements"],
        "recommended": ["scope-statement"],
        "enhances": ["usecase-diagram"]
    },
    "wireframe": {
        "required": ["high-level-requirements"],
        "recommended": ["uiux-wireframe"],
        "enhances": ["scope-statement"]
    }
}
```

---

## Appendix B: Glossary

| Term                    | Definition                                                        |
| ----------------------- | ----------------------------------------------------------------- |
| **Constraint**          | A rule defining prerequisites for document generation             |
| **Prerequisite**        | A document that must/should exist before another can be generated |
| **Enforcement Mode**    | Level of strictness for constraint checking                       |
| **Metadata Extraction** | AI process to detect document types in uploaded files             |
| **Happy Path**          | Successful flow where all constraints are satisfied               |
| **Error Path**          | Flow handling constraint violations                               |

---

**Document End**
