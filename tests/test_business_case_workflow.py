# tests/test_business_case_workflow.py
import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from workflows.business_case_workflow.workflow import business_case_graph

def test_business_case_basic_generation():
    """Test basic business case document generation"""
    input_state = {
        "user_message": """
        Project: E-commerce Platform Development
        Problem: Current manual ordering process is inefficient
        Solution: Develop automated e-commerce platform
        Investment: $500,000
        Expected Benefits: 30% revenue increase, 40% time reduction
        Timeline: 6 months
        """
    }
    
    result = business_case_graph.invoke(input_state)
    
    # Verify response structure
    assert "response" in result
    assert "title" in result["response"]
    assert "content" in result["response"]
    
    # Verify content has key sections
    content = result["response"]["content"]
    assert "Business Case" in content or "business case" in content.lower()
    assert len(content) > 100  # Should have substantial content

def test_business_case_with_detailed_input():
    """Test business case generation with detailed requirements"""
    input_state = {
        "user_message": """
        Project Name: Mobile Banking Application
        Problem Statement: Customers lack convenient mobile access to banking services
        Proposed Solution: Develop iOS and Android mobile banking app with core features
        Estimated Investment: $750,000
        Expected Benefits:
        - 50% increase in digital transactions
        - 30% reduction in branch visits
        - Improved customer satisfaction scores
        Timeline: 9 months
        Strategic Alignment: Digital transformation initiative, Customer experience improvement
        """
    }
    
    result = business_case_graph.invoke(input_state)
    
    # Verify response
    assert "response" in result
    assert result["response"]["title"]
    assert result["response"]["content"]
    
    content = result["response"]["content"]
    # Check for key business case sections
    assert any(keyword in content.lower() for keyword in ["problem", "solution", "cost", "benefit", "roi"])

def test_business_case_response_format():
    """Test that business case follows the expected format"""
    input_state = {
        "user_message": "Create a business case for implementing a CRM system costing $200,000"
    }
    
    result = business_case_graph.invoke(input_state)
    
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

def test_business_case_error_handling():
    """Test error handling with minimal input"""
    input_state = {
        "user_message": ""
    }
    
    result = business_case_graph.invoke(input_state)
    
    # Should still return a response (may be error or minimal content)
    assert "response" in result
    assert "title" in result["response"]
    assert "content" in result["response"]

def test_business_case_content_sections():
    """Test that generated business case includes required sections"""
    input_state = {
        "user_message": """
        Create a comprehensive business case for a Data Analytics Platform.
        Investment: $1M, Expected ROI: 250%, Timeline: 12 months.
        """
    }
    
    result = business_case_graph.invoke(input_state)
    content = result["response"]["content"].lower()
    
    # Check for major sections
    expected_sections = [
        "executive summary",
        "problem",
        "solution",
        "cost",
        "benefit",
        "risk"
    ]
    
    # At least some of these sections should be present
    found_sections = sum(1 for section in expected_sections if section in content)
    assert found_sections >= 3, f"Expected at least 3 major sections, found {found_sections}"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
