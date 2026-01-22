# services/constraint_validator.py
"""
Document Constraint Validator

This module provides validation for document prerequisites as defined in the
Document Constraints Specification. The AI service performs lightweight validation
to ensure expected prerequisite content is present before generation.

The Backend is responsible for:
- Enforcing constraints (blocking/warning based on mode)
- Fetching prerequisite document paths from database
- Providing storage_paths to AI service

The AI service (this module) is responsible for:
- Validating that expected prerequisite content was actually loaded
- Logging validation status for debugging
- Raising clear errors back to Backend if required data is missing
"""

from typing import Dict, List, Optional, TypedDict, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class DependencyType(str, Enum):
    """Dependency types as defined in the specification"""
    REQUIRED = "required"     # Must exist before generation (hard block)
    RECOMMENDED = "recommended"  # Should exist for better quality


class DocumentConstraint(TypedDict):
    """Structure for document constraint definition"""
    required: List[str]      # Required prerequisite document types
    recommended: List[str]   # Recommended prerequisite document types


# Complete Document Constraints Matrix from DOCUMENT_CONSTRAINTS_SPECIFICATION.md
DOCUMENT_CONSTRAINTS: Dict[str, DocumentConstraint] = {
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
    
    # Phase 3: Feasibility & Risk Analysis
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
    
    # Phase 7: Testing & QA
    "rtm": {
        "required": ["high-level-requirements", "srs"],
        "recommended": ["scope-statement"]
    },
    
    # Synthesis Documents
    "srs": {
        "required": ["high-level-requirements", "scope-statement"],
        "recommended": ["stakeholder-register", "business-case"]
    },
    
    # Diagram Documents
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


class PrerequisiteValidationResult(TypedDict):
    """Result of prerequisite validation"""
    valid: bool
    document_type: str
    missing_required: List[str]
    missing_recommended: List[str]
    found_documents: List[str]
    message: str


class ConstraintValidationError(Exception):
    """Exception raised when required prerequisites are missing"""
    
    def __init__(self, document_type: str, missing_required: List[str], message: str):
        self.document_type = document_type
        self.missing_required = missing_required
        self.message = message
        super().__init__(self.message)


def get_constraints(document_type: str) -> Optional[DocumentConstraint]:
    """
    Get constraint definition for a document type.
    
    Args:
        document_type: The document type (e.g., "hld-arch", "lld-api")
        
    Returns:
        DocumentConstraint if found, None if unknown document type
    """
    return DOCUMENT_CONSTRAINTS.get(document_type)


def extract_document_identifiers(extracted_text: str) -> List[str]:
    """
    Extract document type identifiers from the extracted_text content.
    
    The get_content_file node formats documents with "### File:" markers.
    This function extracts filenames and attempts to identify document types.
    
    Args:
        extracted_text: Combined content from prerequisite documents
        
    Returns:
        List of identified document type strings
    """
    if not extracted_text:
        return []
    
    found_docs = []
    lines = extracted_text.split('\n')
    
    for line in lines:
        # Check for "### File:" markers from get_content_file
        # Strip whitespace to handle indented text
        stripped_line = line.strip()
        if stripped_line.startswith("### File:"):
            filename = stripped_line.replace("### File:", "").strip()
            # Extract document type from filename
            doc_type = _filename_to_document_type(filename)
            if doc_type and doc_type not in found_docs:
                found_docs.append(doc_type)
    
    # Also check content for common document type indicators
    content_lower = extracted_text.lower()
    for doc_type in DOCUMENT_CONSTRAINTS.keys():
        # Check for document type mentions in content
        normalized = doc_type.replace("-", " ").replace("_", " ")
        if normalized in content_lower or doc_type in content_lower:
            if doc_type not in found_docs:
                found_docs.append(doc_type)
    
    logger.debug(f"Extracted document identifiers: {found_docs}")
    return found_docs


def _filename_to_document_type(filename: str) -> Optional[str]:
    """
    Convert a filename to a document type identifier.
    
    Args:
        filename: The filename (e.g., "high-level-requirements.md")
        
    Returns:
        Document type string or None if not recognized
    """
    # Remove extension
    name = filename.rsplit('.', 1)[0] if '.' in filename else filename
    
    # Normalize
    name = name.lower().strip()
    
    # Check direct match
    if name in DOCUMENT_CONSTRAINTS:
        return name
    
    # Common variations
    variations = {
        "hlr": "high-level-requirements",
        "high_level_requirements": "high-level-requirements",
        "stakeholder_register": "stakeholder-register",
        "business_case": "business-case",
        "scope_statement": "scope-statement",
        "product_roadmap": "product-roadmap",
        "feasibility_study": "feasibility-study",
        "cost_benefit_analysis": "cost-benefit-analysis",
        "risk_register": "risk-register",
        "hld_arch": "hld-arch",
        "hld_cloud": "hld-cloud",
        "hld_tech": "hld-tech",
        "lld_arch": "lld-arch",
        "lld_db": "lld-db",
        "lld_api": "lld-api",
        "lld_pseudo": "lld-pseudo",
        "class_diagram": "class-diagram",
        "usecase_diagram": "usecase-diagram",
        "activity_diagram": "activity-diagram",
        "uiux_wireframe": "uiux-wireframe",
        "uiux_mockup": "uiux-mockup",
        "uiux_prototype": "uiux-prototype",
    }
    
    # Check underscore variations
    normalized_underscore = name.replace("-", "_")
    if normalized_underscore in variations:
        return variations[normalized_underscore]
    
    return None


def validate_prerequisites(
    document_type: str,
    extracted_text: Optional[str] = None,
    storage_paths: Optional[List[str]] = None,
    strict: bool = True
) -> PrerequisiteValidationResult:
    """
    Validate that required and recommended prerequisites are present.
    
    This is a lightweight validation that checks if expected prerequisite
    content was loaded. The Backend is responsible for the actual enforcement.
    
    Args:
        document_type: The document type being generated
        extracted_text: Combined content from prerequisite documents
        storage_paths: List of storage paths that were requested
        strict: If True, raises ConstraintValidationError for missing required
        
    Returns:
        PrerequisiteValidationResult with validation details
        
    Raises:
        ConstraintValidationError: If strict=True and required prerequisites are missing
    """
    constraints = get_constraints(document_type)
    
    # Unknown document type - no constraints to validate
    if constraints is None:
        logger.warning(f"Unknown document type '{document_type}' - no constraints defined")
        return PrerequisiteValidationResult(
            valid=True,
            document_type=document_type,
            missing_required=[],
            missing_recommended=[],
            found_documents=[],
            message=f"No constraints defined for document type '{document_type}'"
        )
    
    required = constraints["required"]
    recommended = constraints["recommended"]
    
    # Entry point documents have no required prerequisites
    if not required and not recommended:
        logger.info(f"Document type '{document_type}' is an entry point - no prerequisites required")
        return PrerequisiteValidationResult(
            valid=True,
            document_type=document_type,
            missing_required=[],
            missing_recommended=[],
            found_documents=[],
            message=f"'{document_type}' is an entry point document - no prerequisites required"
        )
    
    # Determine what documents were actually provided
    found_docs: List[str] = []
    
    # Check storage_paths for document type indicators
    if storage_paths:
        for path in storage_paths:
            filename = path.split('/')[-1]
            doc_type = _filename_to_document_type(filename)
            if doc_type and doc_type not in found_docs:
                found_docs.append(doc_type)
    
    # Also check extracted_text for document markers
    if extracted_text:
        found_in_content = extract_document_identifiers(extracted_text)
        for doc_type in found_in_content:
            if doc_type not in found_docs:
                found_docs.append(doc_type)
    
    # Check for missing required prerequisites
    missing_required = [req for req in required if req not in found_docs]
    missing_recommended = [rec for rec in recommended if rec not in found_docs]
    
    # Determine validity (only REQUIRED blocks generation)
    is_valid = len(missing_required) == 0
    
    # Build message
    if is_valid and not missing_recommended:
        message = f"All prerequisites satisfied for '{document_type}'"
    elif is_valid and missing_recommended:
        message = (
            f"Required prerequisites satisfied for '{document_type}'. "
            f"Recommended documents missing: {', '.join(missing_recommended)}"
        )
    else:
        message = (
            f"Missing required prerequisites for '{document_type}': "
            f"{', '.join(missing_required)}. "
            "Backend should have validated these before calling AI service."
        )
    
    # Log validation result
    log_level = logging.INFO if is_valid else logging.ERROR
    logger.log(log_level, message)
    
    result = PrerequisiteValidationResult(
        valid=is_valid,
        document_type=document_type,
        missing_required=missing_required,
        missing_recommended=missing_recommended,
        found_documents=found_docs,
        message=message
    )
    
    # Raise error if strict mode and missing required
    if strict and not is_valid:
        raise ConstraintValidationError(
            document_type=document_type,
            missing_required=missing_required,
            message=message
        )
    
    return result


def validate_workflow_state(
    state: Dict[str, Any],
    document_type: str,
    strict: bool = False
) -> Dict[str, Any]:
    """
    Validate workflow state has required prerequisites loaded.
    
    This is a convenience wrapper for use as a LangGraph node.
    
    Args:
        state: Workflow state dictionary
        document_type: The document type being generated
        strict: If True, raises error for missing required prerequisites
        
    Returns:
        Updated state with validation_result added
    """
    extracted_text = state.get("extracted_text", "")
    storage_paths = state.get("storage_paths", [])
    
    try:
        validation_result = validate_prerequisites(
            document_type=document_type,
            extracted_text=extracted_text,
            storage_paths=storage_paths,
            strict=strict
        )
        state["constraint_validation"] = validation_result
        
        # Log missing recommended for debugging
        if validation_result["missing_recommended"]:
            logger.info(
                f"Note: Generating '{document_type}' without recommended prerequisites: "
                f"{', '.join(validation_result['missing_recommended'])}"
            )
            
    except ConstraintValidationError as e:
        state["constraint_validation"] = {
            "valid": False,
            "document_type": document_type,
            "missing_required": e.missing_required,
            "error": e.message
        }
        raise
    
    return state


def get_all_document_types() -> List[str]:
    """
    Get list of all known document types.
    
    Returns:
        List of all document type identifiers
    """
    return list(DOCUMENT_CONSTRAINTS.keys())


def get_entry_point_documents() -> List[str]:
    """
    Get list of entry point documents (no required prerequisites).
    
    Returns:
        List of document types that have no required prerequisites
    """
    return [
        doc_type for doc_type, constraints in DOCUMENT_CONSTRAINTS.items()
        if not constraints["required"]
    ]


def get_document_dependencies(document_type: str) -> Optional[Dict[str, List[str]]]:
    """
    Get dependencies for a specific document type.
    
    Args:
        document_type: The document type to look up
        
    Returns:
        Dict with 'required' and 'recommended' lists, or None if unknown type
    """
    constraints = get_constraints(document_type)
    if constraints is None:
        return None
    
    return {
        "required": constraints["required"],
        "recommended": constraints["recommended"]
    }
