# Document Constraints Implementation Guide

## BA Copilot - Technical Implementation Reference

**Version:** 1.0  
**Date:** December 31, 2024  
**Authors:** BA Copilot Team  
**Status:** Active  
**Companion Document:** [DOCUMENT_CONSTRAINTS_SPECIFICATION.md](./DOCUMENT_CONSTRAINTS_SPECIFICATION.md)

---

## 1. Overview

This guide provides detailed implementation instructions for the Document Constraint System across both Backend (FastAPI) and AI (LangGraph) services. The Backend is the **primary enforcer** of constraints, while the AI service provides **enhanced prompts** and **context validation**.

### 1.1 Responsibility Matrix

| Component      | Responsibilities                                                                    |
| -------------- | ----------------------------------------------------------------------------------- |
| **Backend**    | Constraint definition, prerequisite checking, error responses, WebSocket validation |
| **AI Service** | Context validation, enhanced prompts, quality warnings                              |
| **Database**   | Metadata storage, document type tracking                                            |
| **Frontend**   | Error display, user guidance, constraint override UI                                |

---

## 2. Backend Implementation

### 2.1 File Structure

```
ba_copilot_backend/
├── app/
│   ├── core/
│   │   ├── config.py              # Add constraint config
│   │   └── document_constraints.py # NEW: Constraint definitions
│   ├── services/
│   │   └── constraint_service.py   # NEW: Constraint checking logic
│   ├── utils/
│   │   └── metadata_utils.py       # Add constraint helpers
│   ├── schemas/
│   │   └── constraint_schemas.py   # NEW: Pydantic models
│   └── api/v1/
│       ├── srs.py                  # Add constraint checks
│       ├── diagram.py             # Add constraint checks
│       ├── planning.py            # Add constraint checks
│       ├── analysis.py            # Add constraint checks
│       ├── design.py              # Add constraint checks
│       └── ws_orchestrator.py     # Add constraint validation
```

### 2.2 Core Constraint Definitions

**File:** `ba_copilot_backend/app/core/document_constraints.py`

```python
"""
Document Constraint Definitions

This module defines all document type constraints including:
- Required prerequisites (hard block if missing)
- Recommended prerequisites (warning if missing)
- Enhancing documents (improve quality if available)
"""

from enum import Enum
from typing import Dict, List, Optional, Set
from dataclasses import dataclass


class EnforcementMode(str, Enum):
    """Constraint enforcement levels."""
    STRICT = "STRICT"       # Block if required missing
    GUIDED = "GUIDED"       # Warn but allow override
    PERMISSIVE = "PERMISSIVE"  # Log only


class DocumentPhase(int, Enum):
    """SDLC phases for document organization."""
    PROJECT_INITIATION = 1
    BUSINESS_PLANNING = 2
    FEASIBILITY_RISK = 3
    HIGH_LEVEL_DESIGN = 4
    LOW_LEVEL_DESIGN = 5
    UIUX_DESIGN = 6
    TESTING_QA = 7
    SYNTHESIS = 8
    DIAGRAMS = 9


@dataclass
class DocumentConstraint:
    """Constraint definition for a document type."""
    doc_type: str
    display_name: str
    phase: DocumentPhase
    required: List[str]
    recommended: List[str]
    enhances: List[str]
    description: str
    category: str  # "planning", "analysis", "design", "srs", "diagram"


# =============================================================================
# CONSTRAINT DEFINITIONS
# =============================================================================

DOCUMENT_CONSTRAINTS: Dict[str, DocumentConstraint] = {
    # -------------------------------------------------------------------------
    # Phase 1: Project Initiation (Entry Points - No Required Prerequisites)
    # -------------------------------------------------------------------------
    "stakeholder-register": DocumentConstraint(
        doc_type="stakeholder-register",
        display_name="Stakeholder Register",
        phase=DocumentPhase.PROJECT_INITIATION,
        required=[],
        recommended=[],
        enhances=[],
        description="Registry of all project stakeholders with roles and interests",
        category="planning"
    ),
    "high-level-requirements": DocumentConstraint(
        doc_type="high-level-requirements",
        display_name="High-Level Requirements",
        phase=DocumentPhase.PROJECT_INITIATION,
        required=[],
        recommended=["stakeholder-register"],
        enhances=[],
        description="High-level functional and non-functional requirements",
        category="planning"
    ),
    "requirements-management-plan": DocumentConstraint(
        doc_type="requirements-management-plan",
        display_name="Requirements Management Plan",
        phase=DocumentPhase.PROJECT_INITIATION,
        required=[],
        recommended=["stakeholder-register", "high-level-requirements"],
        enhances=[],
        description="Plan for managing requirements throughout the project",
        category="planning"
    ),

    # -------------------------------------------------------------------------
    # Phase 2: Business Planning
    # -------------------------------------------------------------------------
    "business-case": DocumentConstraint(
        doc_type="business-case",
        display_name="Business Case",
        phase=DocumentPhase.BUSINESS_PLANNING,
        required=["stakeholder-register"],
        recommended=["high-level-requirements"],
        enhances=["scope-statement"],
        description="Business justification with cost-benefit analysis",
        category="planning"
    ),
    "scope-statement": DocumentConstraint(
        doc_type="scope-statement",
        display_name="Scope Statement",
        phase=DocumentPhase.BUSINESS_PLANNING,
        required=["high-level-requirements"],
        recommended=["stakeholder-register", "business-case"],
        enhances=[],
        description="Project scope, boundaries, and deliverables",
        category="planning"
    ),
    "product-roadmap": DocumentConstraint(
        doc_type="product-roadmap",
        display_name="Product Roadmap",
        phase=DocumentPhase.BUSINESS_PLANNING,
        required=["scope-statement"],
        recommended=["business-case", "high-level-requirements"],
        enhances=[],
        description="Timeline of planned features and releases",
        category="planning"
    ),

    # -------------------------------------------------------------------------
    # Phase 3: Feasibility & Risk Analysis
    # -------------------------------------------------------------------------
    "feasibility-study": DocumentConstraint(
        doc_type="feasibility-study",
        display_name="Feasibility Study",
        phase=DocumentPhase.FEASIBILITY_RISK,
        required=["business-case", "scope-statement"],
        recommended=["high-level-requirements"],
        enhances=[],
        description="Technical, economic, and operational feasibility analysis",
        category="analysis"
    ),
    "cost-benefit-analysis": DocumentConstraint(
        doc_type="cost-benefit-analysis",
        display_name="Cost-Benefit Analysis",
        phase=DocumentPhase.FEASIBILITY_RISK,
        required=["business-case"],
        recommended=["feasibility-study", "scope-statement"],
        enhances=[],
        description="Financial analysis comparing costs against benefits",
        category="analysis"
    ),
    "risk-register": DocumentConstraint(
        doc_type="risk-register",
        display_name="Risk Register",
        phase=DocumentPhase.FEASIBILITY_RISK,
        required=["scope-statement"],
        recommended=["feasibility-study", "stakeholder-register"],
        enhances=[],
        description="Identified risks with mitigation strategies",
        category="analysis"
    ),
    "compliance": DocumentConstraint(
        doc_type="compliance",
        display_name="Compliance Document",
        phase=DocumentPhase.FEASIBILITY_RISK,
        required=["scope-statement"],
        recommended=["risk-register", "high-level-requirements"],
        enhances=[],
        description="Regulatory and compliance requirements checklist",
        category="analysis"
    ),

    # -------------------------------------------------------------------------
    # Phase 4: High-Level Design
    # -------------------------------------------------------------------------
    "hld-arch": DocumentConstraint(
        doc_type="hld-arch",
        display_name="System Architecture (HLD)",
        phase=DocumentPhase.HIGH_LEVEL_DESIGN,
        required=["high-level-requirements", "scope-statement"],
        recommended=["feasibility-study"],
        enhances=[],
        description="High-level system architecture and components",
        category="design"
    ),
    "hld-cloud": DocumentConstraint(
        doc_type="hld-cloud",
        display_name="Cloud Infrastructure Design",
        phase=DocumentPhase.HIGH_LEVEL_DESIGN,
        required=["hld-arch"],
        recommended=["feasibility-study", "cost-benefit-analysis"],
        enhances=[],
        description="Cloud deployment architecture and infrastructure",
        category="design"
    ),
    "hld-tech": DocumentConstraint(
        doc_type="hld-tech",
        display_name="Technology Stack Selection",
        phase=DocumentPhase.HIGH_LEVEL_DESIGN,
        required=["hld-arch"],
        recommended=["cost-benefit-analysis"],
        enhances=[],
        description="Technology stack selection with justification",
        category="design"
    ),

    # -------------------------------------------------------------------------
    # Phase 5: Low-Level Design
    # -------------------------------------------------------------------------
    "lld-arch": DocumentConstraint(
        doc_type="lld-arch",
        display_name="Detailed Architecture (LLD)",
        phase=DocumentPhase.LOW_LEVEL_DESIGN,
        required=["hld-arch"],
        recommended=["hld-tech"],
        enhances=[],
        description="Detailed component-level architecture",
        category="design"
    ),
    "lld-db": DocumentConstraint(
        doc_type="lld-db",
        display_name="Database Schema Design",
        phase=DocumentPhase.LOW_LEVEL_DESIGN,
        required=["hld-arch", "high-level-requirements"],
        recommended=["lld-arch"],
        enhances=[],
        description="Database schema with tables and relationships",
        category="design"
    ),
    "lld-api": DocumentConstraint(
        doc_type="lld-api",
        display_name="API Specifications",
        phase=DocumentPhase.LOW_LEVEL_DESIGN,
        required=["hld-arch", "high-level-requirements"],
        recommended=["lld-arch", "lld-db"],
        enhances=[],
        description="API endpoints and specifications",
        category="design"
    ),
    "lld-pseudo": DocumentConstraint(
        doc_type="lld-pseudo",
        display_name="Pseudocode Documentation",
        phase=DocumentPhase.LOW_LEVEL_DESIGN,
        required=["lld-arch"],
        recommended=["lld-api"],
        enhances=[],
        description="Algorithmic pseudocode for key components",
        category="design"
    ),

    # -------------------------------------------------------------------------
    # Phase 6: UI/UX Design
    # -------------------------------------------------------------------------
    "uiux-wireframe": DocumentConstraint(
        doc_type="uiux-wireframe",
        display_name="UI/UX Wireframe",
        phase=DocumentPhase.UIUX_DESIGN,
        required=["high-level-requirements"],
        recommended=["scope-statement", "stakeholder-register"],
        enhances=[],
        description="Low-fidelity wireframes and layouts",
        category="design"
    ),
    "uiux-mockup": DocumentConstraint(
        doc_type="uiux-mockup",
        display_name="UI/UX Mockup",
        phase=DocumentPhase.UIUX_DESIGN,
        required=["uiux-wireframe"],
        recommended=["hld-arch"],
        enhances=[],
        description="High-fidelity visual designs",
        category="design"
    ),
    "uiux-prototype": DocumentConstraint(
        doc_type="uiux-prototype",
        display_name="UI/UX Prototype",
        phase=DocumentPhase.UIUX_DESIGN,
        required=["uiux-mockup"],
        recommended=["uiux-wireframe", "lld-api"],
        enhances=[],
        description="Interactive prototype specifications",
        category="design"
    ),

    # -------------------------------------------------------------------------
    # Phase 7: Testing & QA
    # -------------------------------------------------------------------------
    "rtm": DocumentConstraint(
        doc_type="rtm",
        display_name="Requirements Traceability Matrix",
        phase=DocumentPhase.TESTING_QA,
        required=["high-level-requirements", "srs"],
        recommended=["scope-statement"],
        enhances=[],
        description="Matrix linking requirements to test cases",
        category="srs"
    ),

    # -------------------------------------------------------------------------
    # Synthesis Documents
    # -------------------------------------------------------------------------
    "srs": DocumentConstraint(
        doc_type="srs",
        display_name="Software Requirements Specification",
        phase=DocumentPhase.SYNTHESIS,
        required=["high-level-requirements", "scope-statement"],
        recommended=["stakeholder-register", "business-case"],
        enhances=[],
        description="Comprehensive software requirements specification",
        category="srs"
    ),

    # -------------------------------------------------------------------------
    # Diagram Documents
    # -------------------------------------------------------------------------
    "class-diagram": DocumentConstraint(
        doc_type="class-diagram",
        display_name="Class Diagram",
        phase=DocumentPhase.DIAGRAMS,
        required=["high-level-requirements"],
        recommended=["lld-arch", "lld-db"],
        enhances=["srs"],
        description="UML class diagram showing system classes",
        category="diagram"
    ),
    "usecase-diagram": DocumentConstraint(
        doc_type="usecase-diagram",
        display_name="Use Case Diagram",
        phase=DocumentPhase.DIAGRAMS,
        required=["high-level-requirements"],
        recommended=["stakeholder-register"],
        enhances=["srs"],
        description="UML use case diagram showing actors and interactions",
        category="diagram"
    ),
    "activity-diagram": DocumentConstraint(
        doc_type="activity-diagram",
        display_name="Activity Diagram",
        phase=DocumentPhase.DIAGRAMS,
        required=["high-level-requirements"],
        recommended=["scope-statement"],
        enhances=["usecase-diagram"],
        description="UML activity diagram showing workflow",
        category="diagram"
    ),
    "wireframe": DocumentConstraint(
        doc_type="wireframe",
        display_name="Wireframe",
        phase=DocumentPhase.DIAGRAMS,
        required=["high-level-requirements"],
        recommended=["uiux-wireframe"],
        enhances=["scope-statement"],
        description="UI wireframe or layout design",
        category="diagram"
    ),

    # -------------------------------------------------------------------------
    # Additional Diagram Types (from diagram.py)
    # -------------------------------------------------------------------------
    "sequence": DocumentConstraint(
        doc_type="sequence",
        display_name="Sequence Diagram",
        phase=DocumentPhase.DIAGRAMS,
        required=["high-level-requirements"],
        recommended=["lld-api", "usecase-diagram"],
        enhances=[],
        description="UML sequence diagram showing object interactions",
        category="diagram"
    ),
    "architecture": DocumentConstraint(
        doc_type="architecture",
        display_name="Architecture Diagram",
        phase=DocumentPhase.DIAGRAMS,
        required=["high-level-requirements"],
        recommended=["hld-arch"],
        enhances=[],
        description="System architecture diagram",
        category="diagram"
    ),
    "flowchart": DocumentConstraint(
        doc_type="flowchart",
        display_name="Flowchart",
        phase=DocumentPhase.DIAGRAMS,
        required=["high-level-requirements"],
        recommended=["scope-statement"],
        enhances=[],
        description="Process flowchart diagram",
        category="diagram"
    ),
}


# =============================================================================
# ENTRY POINT DOCUMENTS (No required prerequisites)
# =============================================================================

ENTRY_POINT_DOCUMENTS: Set[str] = {
    "stakeholder-register",
    "high-level-requirements",
    "requirements-management-plan",
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_constraint(doc_type: str) -> Optional[DocumentConstraint]:
    """Get constraint definition for a document type."""
    return DOCUMENT_CONSTRAINTS.get(doc_type)


def get_required_prerequisites(doc_type: str) -> List[str]:
    """Get required prerequisites for a document type."""
    constraint = get_constraint(doc_type)
    return constraint.required if constraint else []


def get_recommended_prerequisites(doc_type: str) -> List[str]:
    """Get recommended prerequisites for a document type."""
    constraint = get_constraint(doc_type)
    return constraint.recommended if constraint else []


def get_all_prerequisites(doc_type: str) -> List[str]:
    """Get all prerequisites (required + recommended + enhances)."""
    constraint = get_constraint(doc_type)
    if not constraint:
        return []
    return constraint.required + constraint.recommended + constraint.enhances


def is_entry_point(doc_type: str) -> bool:
    """Check if document type is an entry point (no required prerequisites)."""
    return doc_type in ENTRY_POINT_DOCUMENTS


def get_display_name(doc_type: str) -> str:
    """Get human-readable display name for a document type."""
    constraint = get_constraint(doc_type)
    return constraint.display_name if constraint else doc_type.replace("-", " ").title()


def get_documents_by_phase(phase: DocumentPhase) -> List[str]:
    """Get all document types in a specific phase."""
    return [
        doc_type for doc_type, constraint in DOCUMENT_CONSTRAINTS.items()
        if constraint.phase == phase
    ]


def get_documents_by_category(category: str) -> List[str]:
    """Get all document types in a specific category."""
    return [
        doc_type for doc_type, constraint in DOCUMENT_CONSTRAINTS.items()
        if constraint.category == category
    ]
```

### 2.3 Constraint Schemas

**File:** `ba_copilot_backend/app/schemas/constraint_schemas.py`

```python
"""
Pydantic schemas for constraint checking API.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class EnforcementMode(str, Enum):
    STRICT = "STRICT"
    GUIDED = "GUIDED"
    PERMISSIVE = "PERMISSIVE"


class SuggestionAction(str, Enum):
    GENERATE = "generate"
    UPLOAD = "upload"
    OVERRIDE = "override"


class ConstraintSuggestion(BaseModel):
    """Suggested action for resolving missing prerequisite."""
    action: SuggestionAction
    doc_type: str
    display_name: str
    endpoint: Optional[str] = None
    description: Optional[str] = None


class ConstraintCheckResult(BaseModel):
    """Result of checking prerequisites for a document type."""
    doc_type: str
    display_name: str
    satisfied: bool
    enforcement_mode: EnforcementMode

    # Missing prerequisites
    missing_required: List[str] = Field(default_factory=list)
    missing_recommended: List[str] = Field(default_factory=list)

    # Available context
    available_docs: List[str] = Field(default_factory=list)
    available_storage_paths: List[str] = Field(default_factory=list)

    # User guidance
    suggestions: List[ConstraintSuggestion] = Field(default_factory=list)
    error_message: Optional[str] = None
    warning_message: Optional[str] = None

    class Config:
        use_enum_values = True


class ConstraintErrorResponse(BaseModel):
    """Error response when prerequisites are missing."""
    error: str = "PREREQUISITE_MISSING"
    message: str
    details: ConstraintCheckResult


class ConstraintWarningResponse(BaseModel):
    """Warning response when recommended prerequisites are missing."""
    warning: str = "RECOMMENDED_MISSING"
    message: str
    details: ConstraintCheckResult


class ProjectDocumentStatus(BaseModel):
    """Summary of available documents in a project."""
    project_id: int
    available_types: List[str]
    ai_generated: List[str]
    user_uploaded: List[str]
    total_count: int


class ConstraintValidationRequest(BaseModel):
    """Request to validate constraints for document generation."""
    doc_type: str
    project_id: int
    override: bool = False
    override_reason: Optional[str] = None
```

### 2.4 Constraint Service

**File:** `ba_copilot_backend/app/services/constraint_service.py`

```python
"""
Constraint Service

Handles all constraint checking logic including:
- Querying project documents from database
- Checking prerequisites against constraints
- Building suggestions for missing prerequisites
"""

import logging
from typing import List, Optional, Set, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.document_constraints import (
    DOCUMENT_CONSTRAINTS,
    get_constraint,
    get_display_name,
    is_entry_point,
    EnforcementMode,
)
from app.schemas.constraint_schemas import (
    ConstraintCheckResult,
    ConstraintSuggestion,
    SuggestionAction,
    ProjectDocumentStatus,
)
from app.models.files import Files
from app.core.config import settings

logger = logging.getLogger(__name__)


class ConstraintService:
    """Service for checking document constraints."""

    def __init__(self, db: Session):
        self.db = db
        self.enforcement_mode = EnforcementMode(
            getattr(settings, 'CONSTRAINT_ENFORCEMENT_MODE', 'GUIDED')
        )

    def get_project_document_types(self, project_id: int) -> ProjectDocumentStatus:
        """
        Get all document types available in a project.

        Checks both:
        1. AI-generated documents (file_category = 'ai generated')
        2. User uploads with detected metadata
        """
        # Query all files for the project
        files = self.db.query(Files).filter(
            Files.project_id == project_id,
            Files.status == 'active'
        ).all()

        available_types: Set[str] = set()
        ai_generated: Set[str] = set()
        user_uploaded: Set[str] = set()

        for file in files:
            # Check AI-generated documents
            if file.file_category == 'ai generated':
                doc_type = file.file_type
                if doc_type in DOCUMENT_CONSTRAINTS:
                    available_types.add(doc_type)
                    ai_generated.add(doc_type)

            # Check user uploads with metadata extraction
            elif file.file_category == 'user upload' and file.metadata:
                metadata = file.metadata

                # Check for extracted document types
                if 'document_types' in metadata:
                    for dt_info in metadata['document_types']:
                        if isinstance(dt_info, dict) and 'type' in dt_info:
                            # Only count if detected (line_start != -1)
                            if dt_info.get('line_start', -1) != -1:
                                doc_type = dt_info['type']
                                if doc_type in DOCUMENT_CONSTRAINTS:
                                    available_types.add(doc_type)
                                    user_uploaded.add(doc_type)
                        elif isinstance(dt_info, str):
                            if dt_info in DOCUMENT_CONSTRAINTS:
                                available_types.add(dt_info)
                                user_uploaded.add(dt_info)

                # Check for manual tags
                if 'manual_tags' in metadata:
                    for tag in metadata['manual_tags']:
                        if tag in DOCUMENT_CONSTRAINTS:
                            available_types.add(tag)
                            user_uploaded.add(tag)

        return ProjectDocumentStatus(
            project_id=project_id,
            available_types=list(available_types),
            ai_generated=list(ai_generated),
            user_uploaded=list(user_uploaded),
            total_count=len(available_types)
        )

    def get_document_storage_paths(
        self,
        project_id: int,
        doc_types: List[str]
    ) -> List[str]:
        """
        Get storage paths for specific document types in a project.

        Returns paths that can be passed to AI service for context.
        """
        storage_paths = []

        for doc_type in doc_types:
            # First try AI-generated
            file = self.db.query(Files).filter(
                Files.project_id == project_id,
                Files.status == 'active',
                Files.file_type == doc_type,
                Files.file_category == 'ai generated'
            ).order_by(Files.created_at.desc()).first()

            if file:
                # Prefer markdown path if available
                path = file.storage_md_path or file.storage_path
                if path:
                    storage_paths.append(path)
                continue

            # Then try user uploads with matching metadata
            files = self.db.query(Files).filter(
                Files.project_id == project_id,
                Files.status == 'active',
                Files.file_category == 'user upload'
            ).all()

            for f in files:
                if f.metadata and 'document_types' in f.metadata:
                    for dt_info in f.metadata['document_types']:
                        dt = dt_info.get('type') if isinstance(dt_info, dict) else dt_info
                        if dt == doc_type:
                            path = f.storage_md_path or f.storage_path
                            if path:
                                storage_paths.append(path)
                            break

        return storage_paths

    def check_prerequisites(
        self,
        doc_type: str,
        project_id: int,
        additional_available: Optional[List[str]] = None
    ) -> ConstraintCheckResult:
        """
        Check if all prerequisites are met for generating a document type.

        Args:
            doc_type: The document type to generate
            project_id: The project ID
            additional_available: Additional doc types to consider available
                                 (useful for WebSocket multi-step generation)

        Returns:
            ConstraintCheckResult with satisfaction status and details
        """
        constraint = get_constraint(doc_type)

        if not constraint:
            logger.warning(f"No constraint defined for doc_type: {doc_type}")
            return ConstraintCheckResult(
                doc_type=doc_type,
                display_name=doc_type.replace("-", " ").title(),
                satisfied=True,
                enforcement_mode=self.enforcement_mode,
                warning_message=f"No constraints defined for {doc_type}"
            )

        # Get available documents in project
        project_docs = self.get_project_document_types(project_id)
        available_set = set(project_docs.available_types)

        # Add any additional available docs (from earlier generation steps)
        if additional_available:
            available_set.update(additional_available)

        # Check required prerequisites
        missing_required = [
            req for req in constraint.required
            if req not in available_set
        ]

        # Check recommended prerequisites
        missing_recommended = [
            rec for rec in constraint.recommended
            if rec not in available_set
        ]

        # Determine satisfaction
        satisfied = len(missing_required) == 0

        # Build suggestions
        suggestions = self._build_suggestions(missing_required, missing_recommended)

        # Build messages
        error_message = None
        warning_message = None

        if missing_required:
            missing_names = [get_display_name(m) for m in missing_required]
            error_message = (
                f"Cannot generate {constraint.display_name}. "
                f"Required prerequisites missing: {', '.join(missing_names)}"
            )

        if missing_recommended:
            missing_names = [get_display_name(m) for m in missing_recommended]
            warning_message = (
                f"Generating {constraint.display_name} without recommended prerequisites: "
                f"{', '.join(missing_names)}. Output quality may be affected."
            )

        # Get storage paths for available prerequisite documents
        all_prereqs = constraint.required + constraint.recommended + constraint.enhances
        available_prereqs = [p for p in all_prereqs if p in available_set]
        storage_paths = self.get_document_storage_paths(project_id, available_prereqs)

        return ConstraintCheckResult(
            doc_type=doc_type,
            display_name=constraint.display_name,
            satisfied=satisfied,
            enforcement_mode=self.enforcement_mode,
            missing_required=missing_required,
            missing_recommended=missing_recommended,
            available_docs=list(available_set),
            available_storage_paths=storage_paths,
            suggestions=suggestions,
            error_message=error_message,
            warning_message=warning_message
        )

    def _build_suggestions(
        self,
        missing_required: List[str],
        missing_recommended: List[str]
    ) -> List[ConstraintSuggestion]:
        """Build actionable suggestions for missing prerequisites."""
        suggestions = []

        # Suggestions for required documents
        for doc_type in missing_required:
            constraint = get_constraint(doc_type)

            # Suggest generation
            suggestions.append(ConstraintSuggestion(
                action=SuggestionAction.GENERATE,
                doc_type=doc_type,
                display_name=get_display_name(doc_type),
                endpoint=f"/api/v1/{constraint.category}/generate" if constraint else None,
                description=f"Generate {get_display_name(doc_type)} first"
            ))

            # Suggest upload
            suggestions.append(ConstraintSuggestion(
                action=SuggestionAction.UPLOAD,
                doc_type=doc_type,
                display_name=get_display_name(doc_type),
                endpoint="/api/v1/files/upload",
                description=f"Upload existing {get_display_name(doc_type)}"
            ))

        # Suggestions for recommended documents (generate only)
        for doc_type in missing_recommended:
            constraint = get_constraint(doc_type)
            suggestions.append(ConstraintSuggestion(
                action=SuggestionAction.GENERATE,
                doc_type=doc_type,
                display_name=get_display_name(doc_type),
                endpoint=f"/api/v1/{constraint.category}/generate" if constraint else None,
                description=f"Generate {get_display_name(doc_type)} for better quality"
            ))

        return suggestions

    def validate_generation_request(
        self,
        doc_type: str,
        project_id: int,
        allow_override: bool = False,
        additional_available: Optional[List[str]] = None
    ) -> Tuple[bool, Optional[ConstraintCheckResult]]:
        """
        Validate a document generation request against constraints.

        Returns:
            Tuple of (can_proceed, constraint_result)
            - can_proceed: True if generation should proceed
            - constraint_result: Details if blocked or has warnings
        """
        result = self.check_prerequisites(doc_type, project_id, additional_available)

        if result.satisfied:
            # All required met, check for warnings
            if result.missing_recommended:
                return (True, result)  # Proceed with warning
            return (True, None)  # Proceed without issues

        # Required prerequisites missing
        if self.enforcement_mode == EnforcementMode.STRICT:
            return (False, result)  # Block

        if self.enforcement_mode == EnforcementMode.GUIDED:
            if allow_override:
                return (True, result)  # Proceed with override
            return (False, result)  # Block, but can be overridden

        # PERMISSIVE mode
        logger.warning(
            f"Constraint violation (PERMISSIVE mode): {doc_type} missing {result.missing_required}"
        )
        return (True, result)  # Proceed anyway


def get_constraint_service(db: Session) -> ConstraintService:
    """Factory function to get ConstraintService instance."""
    return ConstraintService(db)
```

### 2.5 Integration with Generation Endpoints

**Example integration in `ba_copilot_backend/app/api/v1/design.py`:**

```python
from fastapi import APIRouter, Depends, HTTPException, Form, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.services.constraint_service import get_constraint_service
from app.schemas.constraint_schemas import ConstraintErrorResponse

router = APIRouter(prefix="/design", tags=["Design Documents"])


@router.post("/generate")
async def generate_design_document(
    doc_type: str = Form(...),
    project_id: int = Form(...),
    description: str = Form(...),
    title: str = Form(None),
    allow_override: bool = Form(False),  # NEW: Allow constraint override
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Generate a design document with constraint validation."""

    # Validate doc_type
    if doc_type not in VALID_DESIGN_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid doc_type. Must be one of: {VALID_DESIGN_TYPES}"
        )

    # =========================================================================
    # CONSTRAINT CHECKING
    # =========================================================================
    constraint_service = get_constraint_service(db)
    can_proceed, constraint_result = constraint_service.validate_generation_request(
        doc_type=doc_type,
        project_id=project_id,
        allow_override=allow_override
    )

    if not can_proceed:
        # Return 422 with constraint details
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "PREREQUISITE_MISSING",
                "message": constraint_result.error_message,
                "details": constraint_result.model_dump()
            }
        )

    # Log warning if proceeding with missing recommended
    if constraint_result and constraint_result.warning_message:
        logger.warning(constraint_result.warning_message)

    # =========================================================================
    # PROCEED WITH GENERATION (existing logic)
    # =========================================================================

    # Get storage paths from constraint result (includes prerequisite docs)
    storage_paths = []
    if constraint_result:
        storage_paths = constraint_result.available_storage_paths
    else:
        # Fallback to existing list_file logic
        user_files = list_file(project_id, db, current_user)
        storage_paths = [f.storage_md_path for f in user_files if f.storage_md_path]

    # Build AI payload with constraint context
    payload = {
        "message": description,
        "storage_paths": storage_paths,
        "content_id": None,
        # NEW: Pass constraint context to AI for enhanced prompts
        "constraint_context": {
            "doc_type": doc_type,
            "available_docs": constraint_result.available_docs if constraint_result else [],
            "missing_recommended": constraint_result.missing_recommended if constraint_result else []
        }
    }

    # Call AI service
    ai_url = getattr(settings, f"AI_{doc_type.upper().replace('-', '_')}_URL")
    response = await call_ai_service(ai_url, payload)

    # ... rest of existing logic (save to storage, create file record, etc.)
```

### 2.6 WebSocket Orchestrator Integration

**Updates to `ba_copilot_backend/app/api/v1/ws_orchestrator.py`:**

```python
async def validate_generation_plan(
    self,
    steps: List[Dict],
    project_id: int,
    db: Session
) -> Tuple[bool, Optional[Dict]]:
    """
    Validate entire generation plan before starting.

    Checks all steps to ensure prerequisites will be satisfied
    as documents are generated in sequence.
    """
    constraint_service = get_constraint_service(db)

    # Track what will be available after each step
    generated_so_far: List[str] = []

    # Get currently available documents
    project_docs = constraint_service.get_project_document_types(project_id)
    generated_so_far.extend(project_docs.available_types)

    validation_errors = []

    for step_idx, step in enumerate(steps):
        step_doc_types = step.get('doc_types', [])

        for doc_type in step_doc_types:
            result = constraint_service.check_prerequisites(
                doc_type=doc_type,
                project_id=project_id,
                additional_available=generated_so_far
            )

            if not result.satisfied:
                validation_errors.append({
                    "step": step_idx + 1,
                    "doc_type": doc_type,
                    "display_name": result.display_name,
                    "missing_required": result.missing_required,
                    "error_message": result.error_message
                })

        # Add this step's documents to generated_so_far for next iteration
        generated_so_far.extend(step_doc_types)

    if validation_errors:
        return (False, {
            "type": "validation_error",
            "message": "Generation plan has unmet prerequisites",
            "errors": validation_errors
        })

    return (True, None)


async def handle_generate_action(self, data: Dict):
    """Handle generate action with upfront validation."""
    steps = data.get('steps', [])
    project_id = data.get('project_id')

    # Validate entire plan first
    is_valid, error = await self.validate_generation_plan(
        steps, project_id, self.db
    )

    if not is_valid:
        await self.send_message(error)
        return

    # Proceed with generation...
```

---

## 3. AI Service Implementation

### 3.1 Enhanced Request Model

**File:** `ba_copilot_ai/models/ai_request.py`

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class ConstraintContext(BaseModel):
    """Context about constraints passed from backend."""
    doc_type: str
    available_docs: List[str] = Field(default_factory=list)
    missing_recommended: List[str] = Field(default_factory=list)


class AIRequest(BaseModel):
    """Enhanced AI request with constraint context."""
    message: str
    content_id: Optional[str] = None
    storage_paths: Optional[List[str]] = None
    constraint_context: Optional[ConstraintContext] = None
```

### 3.2 Constraint-Aware Prompt Templates

**File:** `ba_copilot_ai/prompts/constraint_prompts.py`

```python
"""
Constraint-aware prompt templates for document generation.

These prompts enhance AI output by:
1. Informing the AI about available prerequisite documents
2. Guiding the AI to reference specific sources
3. Handling cases where recommended docs are missing
"""

from typing import List, Dict, Optional


def build_context_preamble(
    available_docs: List[str],
    missing_recommended: List[str],
    doc_type: str
) -> str:
    """
    Build context preamble to prepend to prompts.

    Informs the AI about what context is available and what's missing.
    """
    preamble_parts = []

    # Available documents context
    if available_docs:
        doc_list = ", ".join(available_docs)
        preamble_parts.append(
            f"AVAILABLE CONTEXT: The following prerequisite documents are available "
            f"and have been provided for reference: {doc_list}. "
            f"Please incorporate relevant information from these documents."
        )

    # Missing recommended warning
    if missing_recommended:
        missing_list = ", ".join(missing_recommended)
        preamble_parts.append(
            f"NOTE: The following recommended documents are not available: {missing_list}. "
            f"Generate the best possible output based on available information, "
            f"and clearly indicate any assumptions made due to missing context."
        )

    return "\n\n".join(preamble_parts)


# Document-specific enhanced prompts
CONSTRAINT_AWARE_PROMPTS: Dict[str, str] = {
    "uiux-wireframe": """
{context_preamble}

You are a professional UI/UX Designer creating wireframes for a software project.

Based on the HIGH-LEVEL REQUIREMENTS provided, create comprehensive wireframe specifications.

USER REQUEST:
{message}

REQUIREMENTS:
1. Reference the requirements document to ensure all user-facing features are represented
2. Include navigation flow between screens
3. Specify component layouts and placeholder content
4. Note any accessibility considerations
5. If stakeholder information is available, consider their user personas

OUTPUT FORMAT:
Generate detailed wireframe specifications in markdown format including:
- Screen inventory
- Component hierarchy
- Navigation map
- Responsive breakpoint notes
- Interaction specifications
""",

    "uiux-mockup": """
{context_preamble}

You are a professional UI/UX Designer creating high-fidelity mockup specifications.

Based on the WIREFRAME provided, create detailed mockup design specifications.

USER REQUEST:
{message}

REQUIREMENTS:
1. Reference the wireframe document for layout structure
2. Define color palette, typography, and spacing
3. Specify component styles and states
4. Include visual hierarchy guidelines
5. If architecture documents are available, ensure technical feasibility

OUTPUT FORMAT:
Generate comprehensive mockup specifications in markdown format including:
- Design system tokens (colors, typography, spacing)
- Component specifications
- Visual states (default, hover, active, disabled)
- Responsive adaptations
- Asset requirements
""",

    "lld-db": """
{context_preamble}

You are a professional Database Architect designing a database schema.

Based on the HIGH-LEVEL ARCHITECTURE and REQUIREMENTS, create a detailed database design.

USER REQUEST:
{message}

REQUIREMENTS:
1. Reference architecture documents for system boundaries
2. Derive entities from requirements
3. Define relationships and cardinality
4. Specify indexes for query optimization
5. Include data types and constraints

OUTPUT FORMAT:
Generate a complete database schema in Mermaid ERD format with:
- Entity definitions
- Relationships (1:1, 1:N, M:N)
- Primary and foreign keys
- Important indexes
- Data type specifications
""",

    "srs": """
{context_preamble}

You are a professional Business Analyst creating a Software Requirements Specification.

SYNTHESIZE information from all available prerequisite documents to create a comprehensive SRS.

USER REQUEST:
{message}

REQUIREMENTS:
1. Incorporate stakeholder information for user roles
2. Reference high-level requirements for functional specs
3. Use scope statement for boundaries and constraints
4. Include business case justification where relevant
5. Ensure traceability to source documents

OUTPUT FORMAT:
Generate a complete SRS document following IEEE 830 structure:
1. Introduction (Purpose, Scope, Definitions)
2. Overall Description (Product perspective, functions, constraints)
3. Specific Requirements (Functional, Non-functional)
4. Appendices (References, supporting information)
""",
}


def get_enhanced_prompt(
    doc_type: str,
    message: str,
    available_docs: List[str],
    missing_recommended: List[str]
) -> str:
    """
    Get constraint-aware prompt for a document type.

    Falls back to basic prompt if no enhanced version exists.
    """
    context_preamble = build_context_preamble(
        available_docs, missing_recommended, doc_type
    )

    template = CONSTRAINT_AWARE_PROMPTS.get(doc_type)

    if template:
        return template.format(
            context_preamble=context_preamble,
            message=message
        )

    # Fallback: prepend context to basic message
    if context_preamble:
        return f"{context_preamble}\n\n{message}"

    return message
```

### 3.3 Workflow Integration

**Example update to a workflow node:**

```python
# In workflow generate node
def generate_document(state: DocumentState) -> DocumentState:
    """Generate document with constraint-aware prompting."""
    from prompts.constraint_prompts import get_enhanced_prompt

    # Extract constraint context if provided
    constraint_context = state.get('constraint_context', {})
    available_docs = constraint_context.get('available_docs', [])
    missing_recommended = constraint_context.get('missing_recommended', [])
    doc_type = constraint_context.get('doc_type', state.get('doc_type', ''))

    # Build enhanced prompt
    enhanced_message = get_enhanced_prompt(
        doc_type=doc_type,
        message=state['user_message'],
        available_docs=available_docs,
        missing_recommended=missing_recommended
    )

    # Combine with extracted file content and chat history
    full_prompt = f"""
{state.get('extracted_content', '')}

{state.get('chat_context', '')}

{enhanced_message}
"""

    # Call LLM
    model_client = get_model_client()
    response = model_client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": full_prompt}],
        response_format={"type": "json_object"}
    )

    # ... parse and return response
```

### 3.4 Quality Validation Node

**File:** `ba_copilot_ai/workflows/nodes/validate_context.py`

```python
"""
Context validation node for AI workflows.

Validates that prerequisite document content is sufficient
for quality generation.
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


# Minimum content thresholds by document type
MIN_CONTENT_LENGTH = {
    "high-level-requirements": 200,
    "scope-statement": 300,
    "business-case": 400,
    "hld-arch": 300,
    "uiux-wireframe": 200,
    "default": 100
}


def validate_context(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate that extracted content is sufficient for quality generation.

    Adds warnings to state if content is insufficient but doesn't block.
    """
    warnings: List[Dict] = []
    extracted_content = state.get('extracted_content', '')
    constraint_context = state.get('constraint_context', {})
    doc_type = constraint_context.get('doc_type', '')
    available_docs = constraint_context.get('available_docs', [])

    # Check overall content length
    if len(extracted_content) < MIN_CONTENT_LENGTH.get('default', 100):
        warnings.append({
            "code": "MINIMAL_CONTEXT",
            "message": "Very little context was extracted from prerequisite documents",
            "suggestion": "Consider adding more detail to your uploaded documents"
        })

    # Check for specific document types
    for req_doc in available_docs:
        min_length = MIN_CONTENT_LENGTH.get(req_doc, 100)

        # Simple heuristic: check if doc type is mentioned in content
        # (In production, would need smarter content attribution)
        if req_doc.replace('-', ' ') not in extracted_content.lower():
            if req_doc.replace('-', '_') not in extracted_content.lower():
                warnings.append({
                    "code": "MISSING_EXPECTED_CONTENT",
                    "message": f"Content from {req_doc} may not have been properly extracted",
                    "suggestion": f"Ensure {req_doc} document contains relevant information"
                })

    # Add warnings to state
    state['context_warnings'] = warnings

    if warnings:
        logger.warning(f"Context validation warnings for {doc_type}: {warnings}")

    return state
```

---

## 4. API Contracts

### 4.1 Constraint Check Endpoint

**New endpoint for frontend to check constraints before generation:**

```python
@router.get("/constraints/check/{project_id}/{doc_type}")
async def check_constraints(
    project_id: int,
    doc_type: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> ConstraintCheckResult:
    """
    Check if prerequisites are met for generating a document type.

    Use this endpoint to:
    1. Display prerequisite status to user before generation
    2. Get suggestions for missing prerequisites
    3. Determine if generation should be blocked or warned
    """
    constraint_service = get_constraint_service(db)
    return constraint_service.check_prerequisites(doc_type, project_id)
```

### 4.2 Project Document Status Endpoint

```python
@router.get("/constraints/status/{project_id}")
async def get_project_document_status(
    project_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> ProjectDocumentStatus:
    """
    Get summary of all available documents in a project.

    Returns lists of AI-generated and user-uploaded document types.
    """
    constraint_service = get_constraint_service(db)
    return constraint_service.get_project_document_types(project_id)
```

### 4.3 Error Response Contract

**HTTP 422 Response for Missing Prerequisites:**

```json
{
  "detail": {
    "error": "PREREQUISITE_MISSING",
    "message": "Cannot generate UI/UX Mockup. Required prerequisites missing: UI/UX Wireframe",
    "details": {
      "doc_type": "uiux-mockup",
      "display_name": "UI/UX Mockup",
      "satisfied": false,
      "enforcement_mode": "GUIDED",
      "missing_required": ["uiux-wireframe"],
      "missing_recommended": ["hld-arch"],
      "available_docs": ["high-level-requirements", "scope-statement"],
      "available_storage_paths": [
        "uploads/2/1/high-level-requirements.md",
        "uploads/2/1/scope-statement.md"
      ],
      "suggestions": [
        {
          "action": "generate",
          "doc_type": "uiux-wireframe",
          "display_name": "UI/UX Wireframe",
          "endpoint": "/api/v1/design/generate",
          "description": "Generate UI/UX Wireframe first"
        },
        {
          "action": "upload",
          "doc_type": "uiux-wireframe",
          "display_name": "UI/UX Wireframe",
          "endpoint": "/api/v1/files/upload",
          "description": "Upload existing UI/UX Wireframe"
        }
      ],
      "error_message": "Cannot generate UI/UX Mockup. Required prerequisites missing: UI/UX Wireframe",
      "warning_message": null
    }
  }
}
```

---

## 5. Configuration

### 5.1 Environment Variables

Add to `ba_copilot_backend/.env`:

```bash
# Constraint System Configuration
CONSTRAINT_ENFORCEMENT_MODE=GUIDED  # STRICT | GUIDED | PERMISSIVE

# Enable AI context validation
AI_CONTEXT_VALIDATION_ENABLED=true

# Minimum content length for valid prerequisite
MIN_PREREQUISITE_CONTENT_LENGTH=100

# Allow admin users to override constraints
ALLOW_CONSTRAINT_OVERRIDE=true
```

### 5.2 Config Module Update

Add to `ba_copilot_backend/app/core/config.py`:

```python
class Settings(BaseSettings):
    # ... existing settings ...

    # Constraint settings
    CONSTRAINT_ENFORCEMENT_MODE: str = "GUIDED"
    AI_CONTEXT_VALIDATION_ENABLED: bool = True
    MIN_PREREQUISITE_CONTENT_LENGTH: int = 100
    ALLOW_CONSTRAINT_OVERRIDE: bool = True
```

---

## 6. Testing Strategy

### 6.1 Unit Tests

```python
# tests/test_constraint_service.py

import pytest
from app.services.constraint_service import ConstraintService
from app.core.document_constraints import DOCUMENT_CONSTRAINTS


class TestConstraintService:

    def test_entry_point_no_prerequisites(self, db_session):
        """Entry point documents should have no required prerequisites."""
        service = ConstraintService(db_session)

        result = service.check_prerequisites("stakeholder-register", project_id=1)

        assert result.satisfied is True
        assert result.missing_required == []

    def test_missing_required_blocks(self, db_session):
        """Missing required prerequisite should block in STRICT mode."""
        service = ConstraintService(db_session)
        service.enforcement_mode = "STRICT"

        # uiux-mockup requires uiux-wireframe
        result = service.check_prerequisites("uiux-mockup", project_id=1)

        assert result.satisfied is False
        assert "uiux-wireframe" in result.missing_required

    def test_suggestions_provided(self, db_session):
        """Should provide suggestions for missing prerequisites."""
        service = ConstraintService(db_session)

        result = service.check_prerequisites("lld-db", project_id=1)

        assert len(result.suggestions) > 0
        assert any(s.action == "generate" for s in result.suggestions)
        assert any(s.action == "upload" for s in result.suggestions)
```

### 6.2 Integration Tests

```python
# tests/integration/test_constraint_flow.py

import pytest
from fastapi.testclient import TestClient


class TestConstraintFlow:

    def test_generate_with_missing_required_returns_422(self, client, auth_headers):
        """Generate request with missing required should return 422."""
        response = client.post(
            "/api/v1/design/generate",
            data={
                "doc_type": "uiux-mockup",
                "project_id": 1,
                "description": "Test mockup"
            },
            headers=auth_headers
        )

        assert response.status_code == 422
        assert response.json()["detail"]["error"] == "PREREQUISITE_MISSING"

    def test_generate_entry_point_succeeds(self, client, auth_headers):
        """Entry point document should generate without prerequisites."""
        response = client.post(
            "/api/v1/planning/generate",
            data={
                "doc_type": "stakeholder-register",
                "project_id": 1,
                "description": "Test stakeholder register"
            },
            headers=auth_headers
        )

        assert response.status_code == 200
```

---

## 7. Migration & Rollout

### 7.1 Phase 1: Backend Foundation (Current)

- [ ] Create `document_constraints.py`
- [ ] Create `constraint_service.py`
- [ ] Create `constraint_schemas.py`
- [ ] Add constraint config to settings

### 7.2 Phase 2: Endpoint Integration

- [ ] Update `design.py` with constraint checks
- [ ] Update `planning.py` with constraint checks
- [ ] Update `analysis.py` with constraint checks
- [ ] Update `srs.py` with constraint checks
- [ ] Update `diagram.py` with constraint checks

### 7.3 Phase 3: WebSocket & API

- [ ] Update `ws_orchestrator.py` with validation
- [ ] Add `/constraints/check` endpoint
- [ ] Add `/constraints/status` endpoint

### 7.4 Phase 4: AI Enhancement

- [ ] Create constraint-aware prompts
- [ ] Add context validation node
- [ ] Update workflow state models

### 7.5 Phase 5: Testing & Documentation

- [ ] Unit tests for constraint service
- [ ] Integration tests for endpoints
- [ ] API documentation update
- [ ] User documentation

---

## 8. Troubleshooting

### 8.1 Common Issues

| Issue                   | Cause                                     | Solution                                  |
| ----------------------- | ----------------------------------------- | ----------------------------------------- |
| Constraint always fails | Document type not in DOCUMENT_CONSTRAINTS | Add constraint definition                 |
| Wrong storage paths     | Metadata not extracted                    | Ensure metadata extraction runs on upload |
| AI ignores context      | Prompt not enhanced                       | Check constraint_context passed to AI     |

### 8.2 Debug Logging

Enable constraint debug logging:

```python
# In constraint_service.py
import logging
logging.getLogger('app.services.constraint_service').setLevel(logging.DEBUG)
```

---

**Document End**
