"""
Unit Tests for Document Constraint Validation

Tests the constraint_validator service and validate_prerequisites node
to ensure document dependency rules are correctly enforced.

Run with: pytest tests/test_constraint_validation.py -v
"""

import pytest
import logging
from typing import Dict, Any

from services.constraint_validator import (
    DOCUMENT_CONSTRAINTS,
    DependencyType,
    ConstraintValidationError,
    validate_prerequisites,
    validate_workflow_state,
    get_constraints,
    get_all_document_types,
    get_entry_point_documents,
    get_document_dependencies,
    extract_document_identifiers,
    _filename_to_document_type
)
from workflows.nodes.validate_prerequisites import (
    create_validation_node,
    validate_prerequisites_generic,
    skip_validation_node,
    validate_hld_arch_prerequisites,
    validate_activity_diagram_prerequisites
)


# ============================================================================
# Test: DOCUMENT_CONSTRAINTS Dictionary Completeness
# ============================================================================

class TestDocumentConstraintsCompleteness:
    """Verify the constraint dictionary is complete and well-formed"""
    
    EXPECTED_DOCUMENT_TYPES = [
        # Phase 1: Project Initiation
        "stakeholder-register",
        "high-level-requirements",
        "requirements-management-plan",
        # Phase 2: Business Planning
        "business-case",
        "scope-statement",
        "product-roadmap",
        # Phase 3: Feasibility & Risk
        "feasibility-study",
        "cost-benefit-analysis",
        "risk-register",
        "compliance",
        # Phase 4: High-Level Design
        "hld-arch",
        "hld-cloud",
        "hld-tech",
        # Phase 5: Low-Level Design
        "lld-arch",
        "lld-db",
        "lld-api",
        "lld-pseudo",
        # Phase 6: UI/UX Design
        "uiux-wireframe",
        "uiux-mockup",
        "uiux-prototype",
        # Phase 7: Testing & QA
        "rtm",
        # Synthesis Documents
        "srs",
        # Diagram Documents
        "class-diagram",
        "usecase-diagram",
        "activity-diagram",
        "wireframe"
    ]

    def test_all_document_types_defined(self):
        """All expected document types should be in DOCUMENT_CONSTRAINTS"""
        for doc_type in self.EXPECTED_DOCUMENT_TYPES:
            assert doc_type in DOCUMENT_CONSTRAINTS, \
                f"Document type '{doc_type}' missing from DOCUMENT_CONSTRAINTS"

    def test_constraint_structure(self):
        """Each constraint should have 'required' and 'recommended' lists"""
        for doc_type, constraints in DOCUMENT_CONSTRAINTS.items():
            assert "required" in constraints, \
                f"'{doc_type}' missing 'required' key"
            assert "recommended" in constraints, \
                f"'{doc_type}' missing 'recommended' key"
            assert isinstance(constraints["required"], list), \
                f"'{doc_type}' required should be a list"
            assert isinstance(constraints["recommended"], list), \
                f"'{doc_type}' recommended should be a list"

    def test_no_self_reference(self):
        """Document should not list itself as a prerequisite"""
        for doc_type, constraints in DOCUMENT_CONSTRAINTS.items():
            assert doc_type not in constraints["required"], \
                f"'{doc_type}' references itself in required"
            assert doc_type not in constraints["recommended"], \
                f"'{doc_type}' references itself in recommended"

    def test_references_valid_document_types(self):
        """All referenced documents should exist in DOCUMENT_CONSTRAINTS"""
        all_types = set(DOCUMENT_CONSTRAINTS.keys())
        for doc_type, constraints in DOCUMENT_CONSTRAINTS.items():
            for req in constraints["required"]:
                assert req in all_types, \
                    f"'{doc_type}' requires unknown type '{req}'"
            for rec in constraints["recommended"]:
                assert rec in all_types, \
                    f"'{doc_type}' recommends unknown type '{rec}'"

    def test_entry_points_have_no_required(self):
        """Entry point documents should have no required prerequisites"""
        entry_points = ["stakeholder-register", "high-level-requirements", "requirements-management-plan"]
        for doc_type in entry_points:
            constraints = DOCUMENT_CONSTRAINTS[doc_type]
            assert constraints["required"] == [], \
                f"Entry point '{doc_type}' should have no required prerequisites"


# ============================================================================
# Test: validate_prerequisites Function
# ============================================================================

class TestValidatePrerequisites:
    """Test the core validate_prerequisites function"""

    def test_entry_point_always_valid(self):
        """Entry point documents should always pass validation"""
        result = validate_prerequisites(
            document_type="stakeholder-register",
            extracted_text="",
            storage_paths=[],
            strict=True
        )
        assert result["valid"] is True
        assert result["missing_required"] == []
        assert "entry point" in result["message"].lower()

    def test_unknown_document_type(self):
        """Unknown document types should pass with warning"""
        result = validate_prerequisites(
            document_type="unknown-doc-type",
            extracted_text="",
            storage_paths=[],
            strict=False
        )
        assert result["valid"] is True
        assert "no constraints defined" in result["message"].lower()

    def test_required_prerequisites_missing_non_strict(self):
        """Missing required prerequisites in non-strict mode should set valid=False"""
        # hld-arch requires high-level-requirements AND scope-statement
        result = validate_prerequisites(
            document_type="hld-arch",
            extracted_text="",
            storage_paths=[],
            strict=False
        )
        assert result["valid"] is False
        assert "high-level-requirements" in result["missing_required"]
        assert "scope-statement" in result["missing_required"]

    def test_required_prerequisites_missing_strict_raises(self):
        """Missing required prerequisites in strict mode should raise error"""
        with pytest.raises(ConstraintValidationError) as exc_info:
            validate_prerequisites(
                document_type="hld-arch",
                extracted_text="",
                storage_paths=[],
                strict=True
            )
        assert "high-level-requirements" in exc_info.value.missing_required
        assert exc_info.value.document_type == "hld-arch"

    def test_required_satisfied_via_storage_paths(self):
        """Prerequisites found via storage_paths should satisfy requirements"""
        result = validate_prerequisites(
            document_type="hld-arch",
            extracted_text="",
            storage_paths=[
                "/project/high-level-requirements.md",
                "/project/scope-statement.md"
            ],
            strict=True
        )
        assert result["valid"] is True
        assert result["missing_required"] == []
        assert "high-level-requirements" in result["found_documents"]
        assert "scope-statement" in result["found_documents"]

    def test_required_satisfied_via_extracted_text(self):
        """Prerequisites found via extracted_text should satisfy requirements"""
        extracted_text = """
        ### File: high-level-requirements.md
        High-level requirements content here...
        
        ### File: scope-statement.md
        Scope statement content here...
        """
        result = validate_prerequisites(
            document_type="hld-arch",
            extracted_text=extracted_text,
            storage_paths=[],
            strict=True
        )
        assert result["valid"] is True
        assert result["missing_required"] == []

    def test_partial_requirements_satisfied(self):
        """Partial satisfaction should still fail for missing required"""
        result = validate_prerequisites(
            document_type="hld-arch",
            extracted_text="### File: high-level-requirements.md\nContent...",
            storage_paths=[],
            strict=False
        )
        assert result["valid"] is False
        assert "scope-statement" in result["missing_required"]
        assert "high-level-requirements" in result["found_documents"]

    def test_recommended_missing_does_not_block(self):
        """Missing recommended prerequisites should not block validation"""
        # activity-diagram requires high-level-requirements, recommends scope-statement
        result = validate_prerequisites(
            document_type="activity-diagram",
            extracted_text="### File: high-level-requirements.md\nContent...",
            storage_paths=[],
            strict=True  # Even in strict mode
        )
        assert result["valid"] is True
        assert "scope-statement" in result["missing_recommended"]

    def test_all_prerequisites_satisfied(self):
        """When all prerequisites are satisfied, result should reflect that"""
        extracted_text = """
        ### File: high-level-requirements.md
        Requirements content...
        
        ### File: scope-statement.md
        Scope content...
        
        ### File: usecase-diagram.md
        Use case content...
        """
        result = validate_prerequisites(
            document_type="activity-diagram",
            extracted_text=extracted_text,
            storage_paths=[],
            strict=True
        )
        assert result["valid"] is True
        assert result["missing_required"] == []
        # usecase-diagram is recommended, not required
        assert "usecase-diagram" in result["found_documents"]


# ============================================================================
# Test: extract_document_identifiers Function
# ============================================================================

class TestExtractDocumentIdentifiers:
    """Test document identifier extraction from text content"""

    def test_empty_text(self):
        """Empty text should return empty list"""
        result = extract_document_identifiers("")
        assert result == []

    def test_none_text(self):
        """None text should return empty list"""
        result = extract_document_identifiers(None)  # type: ignore
        assert result == []

    def test_extract_from_file_markers(self):
        """Should extract document types from ### File: markers"""
        text = """
        ### File: high-level-requirements.md
        Content here
        
        ### File: scope-statement.md
        More content
        """
        result = extract_document_identifiers(text)
        assert "high-level-requirements" in result
        assert "scope-statement" in result

    def test_extract_with_underscore_variants(self):
        """Should handle underscore variants in filenames"""
        text = """
        ### File: hld_arch.md
        Architecture content
        """
        result = extract_document_identifiers(text)
        assert "hld-arch" in result

    def test_no_duplicates(self):
        """Should not return duplicate document types"""
        text = """
        ### File: srs.md
        Some SRS content
        
        ### File: srs.md
        More SRS content
        """
        result = extract_document_identifiers(text)
        assert result.count("srs") == 1


# ============================================================================
# Test: _filename_to_document_type Function
# ============================================================================

class TestFilenameToDocumentType:
    """Test filename to document type conversion"""

    def test_direct_match(self):
        """Exact document type names should match"""
        assert _filename_to_document_type("hld-arch.md") == "hld-arch"
        assert _filename_to_document_type("srs.md") == "srs"
        assert _filename_to_document_type("high-level-requirements.md") == "high-level-requirements"

    def test_underscore_variant(self):
        """Underscore variants should be recognized"""
        assert _filename_to_document_type("hld_arch.md") == "hld-arch"
        assert _filename_to_document_type("high_level_requirements.md") == "high-level-requirements"
        assert _filename_to_document_type("cost_benefit_analysis.md") == "cost-benefit-analysis"

    def test_unknown_filename(self):
        """Unknown filenames should return None"""
        assert _filename_to_document_type("random_file.md") is None
        assert _filename_to_document_type("notes.txt") is None

    def test_case_insensitive(self):
        """Should be case insensitive"""
        assert _filename_to_document_type("HLD-ARCH.MD") == "hld-arch"
        assert _filename_to_document_type("SRS.md") == "srs"


# ============================================================================
# Test: Utility Functions
# ============================================================================

class TestUtilityFunctions:
    """Test utility functions for constraint information"""

    def test_get_constraints(self):
        """get_constraints should return correct constraint dict"""
        constraints = get_constraints("hld-arch")
        assert constraints is not None
        assert "required" in constraints
        assert "recommended" in constraints
        assert "high-level-requirements" in constraints["required"]

    def test_get_constraints_unknown(self):
        """get_constraints should return None for unknown type"""
        assert get_constraints("unknown-type") is None

    def test_get_all_document_types(self):
        """get_all_document_types should return all types"""
        all_types = get_all_document_types()
        assert len(all_types) >= 26  # At least 26 document types
        assert "srs" in all_types
        assert "hld-arch" in all_types

    def test_get_entry_point_documents(self):
        """get_entry_point_documents should return docs with no required"""
        entry_points = get_entry_point_documents()
        assert "stakeholder-register" in entry_points
        assert "high-level-requirements" in entry_points
        # hld-arch is NOT an entry point
        assert "hld-arch" not in entry_points

    def test_get_document_dependencies(self):
        """get_document_dependencies should return dependency info"""
        deps = get_document_dependencies("lld-api")
        assert deps is not None
        assert "hld-arch" in deps["required"]
        assert "high-level-requirements" in deps["required"]
        assert "lld-arch" in deps["recommended"]


# ============================================================================
# Test: validate_workflow_state Function
# ============================================================================

class TestValidateWorkflowState:
    """Test workflow state validation helper"""

    def test_adds_validation_to_state(self):
        """Should add constraint_validation to state"""
        state = {
            "user_message": "Test",
            "extracted_text": "",
            "storage_paths": []
        }
        result = validate_workflow_state(state, "stakeholder-register", strict=False)
        assert "constraint_validation" in result
        assert result["constraint_validation"]["valid"] is True

    def test_preserves_existing_state(self):
        """Should preserve existing state values"""
        state = {
            "user_message": "Test message",
            "content_id": "123",
            "extracted_text": "Some text",
            "storage_paths": ["/path/file.md"]
        }
        result = validate_workflow_state(state, "stakeholder-register", strict=False)
        assert result["user_message"] == "Test message"
        assert result["content_id"] == "123"

    def test_strict_mode_raises(self):
        """Strict mode should raise for missing required"""
        state = {
            "extracted_text": "",
            "storage_paths": []
        }
        with pytest.raises(ConstraintValidationError):
            validate_workflow_state(state, "hld-arch", strict=True)


# ============================================================================
# Test: Validation Node Functions
# ============================================================================

class TestValidationNodes:
    """Test LangGraph validation node functions"""

    def test_create_validation_node(self):
        """create_validation_node should return callable"""
        node = create_validation_node("hld-arch", strict=False)
        assert callable(node)
        assert "hld_arch" in node.__name__

    def test_validation_node_execution(self):
        """Validation node should update state"""
        node = create_validation_node("stakeholder-register", strict=False)
        state: Dict[str, Any] = {
            "user_message": "Test",
            "extracted_text": "",
            "storage_paths": []
        }
        result = node(state)
        assert "constraint_validation" in result
        assert result["constraint_validation"]["valid"] is True

    def test_validate_prerequisites_generic_with_type(self):
        """Generic validator should work with document_type in state"""
        state: Dict[str, Any] = {
            "document_type": "stakeholder-register",
            "extracted_text": "",
            "storage_paths": []
        }
        result = validate_prerequisites_generic(state)
        assert result["constraint_validation"]["valid"] is True

    def test_validate_prerequisites_generic_without_type(self):
        """Generic validator should skip when no document_type"""
        state: Dict[str, Any] = {
            "extracted_text": "",
            "storage_paths": []
        }
        result = validate_prerequisites_generic(state)
        assert result["constraint_validation"]["valid"] is True
        assert "skipped" in result["constraint_validation"]["message"].lower()

    def test_skip_validation_node(self):
        """Skip validation node should always pass"""
        state: Dict[str, Any] = {
            "extracted_text": "",
            "storage_paths": []
        }
        result = skip_validation_node(state)
        assert result["constraint_validation"]["valid"] is True
        assert "skipped" in result["constraint_validation"]["message"].lower()

    def test_prebuilt_hld_arch_validator(self):
        """Pre-built hld-arch validator should work"""
        state: Dict[str, Any] = {
            "extracted_text": "### File: high-level-requirements.md\nContent\n### File: scope-statement.md\nContent",
            "storage_paths": []
        }
        result = validate_hld_arch_prerequisites(state)
        assert result["constraint_validation"]["valid"] is True

    def test_prebuilt_activity_diagram_validator(self):
        """Pre-built activity-diagram validator should work"""
        state: Dict[str, Any] = {
            "extracted_text": "### File: high-level-requirements.md\nContent",
            "storage_paths": []
        }
        result = validate_activity_diagram_prerequisites(state)
        assert result["constraint_validation"]["valid"] is True


# ============================================================================
# Test: ConstraintValidationError Exception
# ============================================================================

class TestConstraintValidationError:
    """Test the custom exception class"""

    def test_exception_properties(self):
        """Exception should have correct properties"""
        error = ConstraintValidationError(
            document_type="hld-arch",
            missing_required=["high-level-requirements", "scope-statement"],
            message="Missing required prerequisites"
        )
        assert error.document_type == "hld-arch"
        assert "high-level-requirements" in error.missing_required
        assert "scope-statement" in error.missing_required
        assert "Missing" in error.message

    def test_exception_string(self):
        """Exception should have readable string representation"""
        error = ConstraintValidationError(
            document_type="test",
            missing_required=["dep1"],
            message="Test error message"
        )
        assert "Test error message" in str(error)


# ============================================================================
# Test: Logging Behavior
# ============================================================================

class TestLoggingBehavior:
    """Test that validation produces appropriate logs"""

    def test_logs_validation_result(self, caplog):
        """Should log validation results"""
        with caplog.at_level(logging.INFO):
            validate_prerequisites(
                document_type="stakeholder-register",
                extracted_text="",
                storage_paths=[],
                strict=False
            )
        assert any("entry point" in record.message.lower() for record in caplog.records)

    def test_logs_missing_required(self, caplog):
        """Should log missing required prerequisites as error"""
        with caplog.at_level(logging.ERROR):
            validate_prerequisites(
                document_type="hld-arch",
                extracted_text="",
                storage_paths=[],
                strict=False
            )
        assert any("missing" in record.message.lower() for record in caplog.records)

    def test_logs_unknown_type_warning(self, caplog):
        """Should log warning for unknown document type"""
        with caplog.at_level(logging.WARNING):
            validate_prerequisites(
                document_type="unknown-type",
                extracted_text="",
                storage_paths=[],
                strict=False
            )
        assert any("unknown" in record.message.lower() for record in caplog.records)


# ============================================================================
# Test: Edge Cases
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_whitespace_only_extracted_text(self):
        """Whitespace-only text should be treated as empty"""
        result = validate_prerequisites(
            document_type="hld-arch",
            extracted_text="   \n\t  \n  ",
            storage_paths=[],
            strict=False
        )
        assert result["valid"] is False
        assert len(result["missing_required"]) > 0

    def test_empty_storage_paths_list(self):
        """Empty storage_paths should not cause errors"""
        result = validate_prerequisites(
            document_type="stakeholder-register",
            extracted_text="",
            storage_paths=[],
            strict=False
        )
        assert result["valid"] is True

    def test_none_storage_paths(self):
        """None storage_paths should be handled gracefully"""
        result = validate_prerequisites(
            document_type="stakeholder-register",
            extracted_text="",
            storage_paths=None,  # type: ignore
            strict=False
        )
        assert result["valid"] is True

    def test_mixed_case_document_type(self):
        """Document type lookup should handle case variations"""
        # Document types are expected in lowercase
        result = validate_prerequisites(
            document_type="HLD-ARCH",  # Uppercase - won't match
            extracted_text="",
            storage_paths=[],
            strict=False
        )
        # Should be treated as unknown
        assert "no constraints defined" in result["message"].lower()

    def test_deeply_nested_paths(self):
        """Should handle deeply nested storage paths"""
        result = validate_prerequisites(
            document_type="hld-arch",
            extracted_text="",
            storage_paths=[
                "/user/1/project/2/folder/3/high-level-requirements.md",
                "/user/1/project/2/folder/3/subfolder/scope-statement.md"
            ],
            strict=True
        )
        assert result["valid"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
