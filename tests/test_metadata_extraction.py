# tests/test_metadata_extraction.py
"""
Test suite for metadata extraction workflow.
"""

import pytest
from workflows.metadata_extraction_workflow import metadata_extraction_graph, extract_metadata
from models.metadata_extraction import ALL_DOCUMENT_TYPES


def test_metadata_extraction_simple():
    """Test metadata extraction with simple content."""
    content = """# Business Case

This is a business case for our project.

## Executive Summary
The project will deliver significant value.

## Financial Analysis
Cost: $100,000
Benefit: $500,000
"""
    
    result = extract_metadata(
        document_id="test-123",
        content=content,
        filename="test.md"
    )
    
    # Verify response structure
    assert "document_id" in result
    assert result["document_id"] == "test-123"
    assert "type" in result
    assert result["type"] == "metadata_extraction"
    assert "response" in result
    
    # Verify all document types are present
    response_types = [item["type"] for item in result["response"]]
    assert len(response_types) == len(ALL_DOCUMENT_TYPES)
    assert set(response_types) == set(ALL_DOCUMENT_TYPES)


def test_metadata_extraction_empty_content():
    """Test metadata extraction with empty content."""
    result = extract_metadata(
        document_id="test-empty",
        content="",
        filename="empty.md"
    )
    
    # All types should be not found (-1, -1)
    for item in result["response"]:
        assert item["line_start"] == -1
        assert item["line_end"] == -1


def test_metadata_extraction_multiple_documents():
    """Test metadata extraction with content containing multiple document types."""
    content = """# Project Charter

This is the project charter.

---

# Scope Statement

This defines the project scope.

---

# Business Case

Financial justification for the project.

---

# Software Requirements Specification

## Functional Requirements
1. User authentication
2. Data management

## Non-Functional Requirements  
- Performance
- Security
"""
    
    result = extract_metadata(
        document_id="test-multi",
        content=content,
        filename="multi.md"
    )
    
    # Verify response
    assert result["document_id"] == "test-multi"
    assert len(result["response"]) == len(ALL_DOCUMENT_TYPES)


def test_metadata_extraction_workflow_invoke():
    """Test invoking the workflow graph directly."""
    state = {
        "document_id": "test-invoke",
        "content": "# Test Document\n\nThis is test content.",
        "filename": "test.md",
        "total_lines": 0,
        "phase1_results": None,
        "phase2_results": None,
        "phase3_results": None,
        "phase4_results": None,
        "phase5_results": None,
        "phase6_results": None,
        "phase7_results": None,
        "additional_results": None,
        "response": None,
    }
    
    result = metadata_extraction_graph.invoke(state)
    
    # Verify state was updated
    assert "response" in result
    assert result["response"] is not None
    assert result["total_lines"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
