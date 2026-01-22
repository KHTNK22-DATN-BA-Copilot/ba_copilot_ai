# workflows/nodes/validate_prerequisites.py
"""
Prerequisite Validation Node

This module provides a reusable LangGraph node for validating document prerequisites
before generation. It integrates with the constraint_validator service to ensure
required context is present.

Usage in workflows:
    from workflows.nodes.validate_prerequisites import create_validation_node
    
    # Create validation node for specific document type
    validate_node = create_validation_node("hld-arch")
    
    # Add to workflow
    workflow.add_node("validate_prerequisites", validate_node)
"""

from typing import Dict, Any, Callable, Optional
import logging
from services.constraint_validator import (
    validate_prerequisites,
    ConstraintValidationError,
    PrerequisiteValidationResult
)

logger = logging.getLogger(__name__)


def create_validation_node(
    document_type: str,
    strict: bool = False
) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """
    Create a validation node function for a specific document type.
    
    This factory function creates a node that can be added to LangGraph workflows
    to validate prerequisites before generation.
    
    Args:
        document_type: The document type being generated (e.g., "hld-arch", "lld-api")
        strict: If True, raises error when required prerequisites are missing.
                If False (default), logs warning but continues.
                
    Returns:
        A callable node function that validates state prerequisites
        
    Example:
        >>> validate_hld = create_validation_node("hld-arch", strict=False)
        >>> workflow.add_node("validate_prerequisites", validate_hld)
    """
    
    def validate_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate prerequisites in workflow state.
        
        Args:
            state: Workflow state dictionary containing:
                - extracted_text: Optional[str] - Content from prerequisite docs
                - storage_paths: Optional[List[str]] - Paths that were requested
                
        Returns:
            Updated state with constraint_validation result added
            
        Raises:
            ConstraintValidationError: If strict=True and required prerequisites missing
        """
        extracted_text = state.get("extracted_text", "")
        storage_paths = state.get("storage_paths", [])
        
        logger.info(f"Validating prerequisites for '{document_type}'")
        
        try:
            validation_result = validate_prerequisites(
                document_type=document_type,
                extracted_text=extracted_text,
                storage_paths=storage_paths,
                strict=strict
            )
            
            # Add validation result to state
            state["constraint_validation"] = dict(validation_result)
            
            # Log helpful information
            if validation_result["valid"]:
                logger.info(
                    f"✅ Prerequisites validated for '{document_type}'. "
                    f"Found: {validation_result['found_documents']}"
                )
            else:
                logger.warning(
                    f"⚠️ Prerequisite validation failed for '{document_type}'. "
                    f"Missing required: {validation_result['missing_required']}"
                )
            
            # Log recommended documents if missing
            if validation_result["missing_recommended"]:
                logger.info(
                    f"ℹ️ Recommended prerequisites not provided: "
                    f"{validation_result['missing_recommended']}"
                )
            
            return state
            
        except ConstraintValidationError as e:
            logger.error(
                f"❌ Constraint validation error for '{document_type}': {e.message}"
            )
            # Add error info to state before re-raising
            state["constraint_validation"] = {
                "valid": False,
                "document_type": document_type,
                "missing_required": e.missing_required,
                "error": e.message
            }
            raise
    
    # Set function name for better debugging
    validate_node.__name__ = f"validate_{document_type.replace('-', '_')}_prerequisites"
    validate_node.__doc__ = f"Validate prerequisites for {document_type} generation"
    
    return validate_node


def validate_prerequisites_generic(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generic validation node that uses document_type from state.
    
    This node reads the document_type from the state dictionary,
    allowing for dynamic validation based on the request.
    
    Args:
        state: Workflow state dictionary containing:
            - document_type: str - The type of document being generated
            - extracted_text: Optional[str] - Content from prerequisite docs
            - storage_paths: Optional[List[str]] - Paths that were requested
            
    Returns:
        Updated state with constraint_validation result added
    """
    document_type = state.get("document_type", "")
    
    if not document_type:
        logger.warning("No document_type in state, skipping prerequisite validation")
        state["constraint_validation"] = {
            "valid": True,
            "document_type": "",
            "missing_required": [],
            "missing_recommended": [],
            "found_documents": [],
            "message": "No document_type specified, validation skipped"
        }
        return state
    
    # Use non-strict mode for generic validation
    validator = create_validation_node(document_type, strict=False)
    return validator(state)


def skip_validation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Placeholder node that skips validation (for testing or permissive mode).
    
    This can be used when validation should be bypassed entirely.
    
    Args:
        state: Workflow state dictionary
        
    Returns:
        State with validation marked as skipped
    """
    logger.info("Prerequisite validation skipped (permissive mode)")
    state["constraint_validation"] = {
        "valid": True,
        "document_type": state.get("document_type", "unknown"),
        "missing_required": [],
        "missing_recommended": [],
        "found_documents": [],
        "message": "Validation skipped (permissive mode)"
    }
    return state


# Pre-built validation nodes for common document types
# These can be imported directly for convenience

validate_hld_arch_prerequisites = create_validation_node("hld-arch", strict=False)
validate_hld_cloud_prerequisites = create_validation_node("hld-cloud", strict=False)
validate_hld_tech_prerequisites = create_validation_node("hld-tech", strict=False)

validate_lld_arch_prerequisites = create_validation_node("lld-arch", strict=False)
validate_lld_db_prerequisites = create_validation_node("lld-db", strict=False)
validate_lld_api_prerequisites = create_validation_node("lld-api", strict=False)
validate_lld_pseudo_prerequisites = create_validation_node("lld-pseudo", strict=False)

validate_srs_prerequisites = create_validation_node("srs", strict=False)
validate_activity_diagram_prerequisites = create_validation_node("activity-diagram", strict=False)
validate_class_diagram_prerequisites = create_validation_node("class-diagram", strict=False)
validate_usecase_diagram_prerequisites = create_validation_node("usecase-diagram", strict=False)
