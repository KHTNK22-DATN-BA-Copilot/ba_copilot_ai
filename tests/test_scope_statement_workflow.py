# tests/test_scope_statement_workflow.py
import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from workflows.scope_statement_workflow.workflow import scope_statement_graph

def test_scope_statement_basic_generation():
    """Test basic scope statement document generation"""
    input_state = {
        "user_message": """
        Project: Customer Portal Development
        Scope: Web-based customer portal with account management and order tracking
        Timeline: 4 months
        Budget: $300,000
        """
    }
    
    result = scope_statement_graph.invoke(input_state)
    
    # Verify response structure
    assert "response" in result
    assert "title" in result["response"]
    assert "content" in result["response"]
    
    # Verify content has key sections
    content = result["response"]["content"]
    assert "scope" in content.lower()
    assert len(content) > 100  # Should have substantial content

def test_scope_statement_with_detailed_requirements():
    """Test scope statement generation with detailed project info"""
    input_state = {
        "user_message": """
        Project Name: Inventory Management System
        In Scope:
        - Real-time inventory tracking
        - Barcode scanning integration
        - Automated reorder alerts
        - Reporting dashboard
        Out of Scope:
        - Integration with legacy ERP
        - Mobile application
        Constraints: Must use existing database infrastructure
        Timeline: 6 months
        """
    }
    
    result = scope_statement_graph.invoke(input_state)
    
    # Verify response
    assert "response" in result
    assert result["response"]["title"]
    assert result["response"]["content"]
    
    content = result["response"]["content"].lower()
    # Check for key scope statement sections
    assert any(keyword in content for keyword in ["in scope", "out of scope", "deliverable"])

def test_scope_statement_response_format():
    """Test that scope statement follows the expected format"""
    input_state = {
        "user_message": "Define project scope for a web application redesign project"
    }
    
    result = scope_statement_graph.invoke(input_state)
    
    # Verify JSON structure
    assert isinstance(result, dict)
    assert "response" in result
    assert isinstance(result["response"], dict)
    assert "title" in result["response"]
    assert "content" in result["response"]
    
    # Verify title format
    title = result["response"]["title"]
    assert isinstance(title, str)
    assert len(title) > 0

def test_scope_statement_error_handling():
    """Test error handling with minimal input"""
    input_state = {
        "user_message": ""
    }
    
    result = scope_statement_graph.invoke(input_state)
    
    # Should still return a response
    assert "response" in result
    assert "title" in result["response"]
    assert "content" in result["response"]

def test_scope_statement_content_sections():
    """Test that generated scope statement includes required sections"""
    input_state = {
        "user_message": """
        Create a detailed project scope statement for an API Gateway implementation.
        Include in-scope, out-of-scope, deliverables, and constraints.
        """
    }
    
    result = scope_statement_graph.invoke(input_state)
    content = result["response"]["content"].lower()
    
    # Check for major sections
    expected_sections = [
        "scope",
        "deliverable",
        "constraint",
        "assumption"
    ]
    
    # At least some of these sections should be present
    found_sections = sum(1 for section in expected_sections if section in content)
    assert found_sections >= 2, f"Expected at least 2 major sections, found {found_sections}"

def test_scope_statement_includes_boundaries():
    """Test that scope statement clearly defines project boundaries"""
    input_state = {
        "user_message": """
        Project: Payment Processing Integration
        Must clearly define what's in scope and out of scope
        """
    }
    
    result = scope_statement_graph.invoke(input_state)
    content = result["response"]["content"].lower()
    
    # Should have clear boundaries
    has_in_scope = "in scope" in content or "included" in content
    has_out_scope = "out of scope" in content or "excluded" in content or "not included" in content
    
    assert has_in_scope or has_out_scope, "Scope statement should define project boundaries"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
