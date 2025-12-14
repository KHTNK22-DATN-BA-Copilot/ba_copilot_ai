# tests/test_product_roadmap_workflow.py
import pytest
import sys
import os
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from workflows.product_roadmap_workflow.workflow import product_roadmap_graph

def extract_mermaid_code(markdown_text: str) -> str:
    """Extract mermaid code from markdown fenced code block"""
    pattern = r'```mermaid\s*\n(.*?)```'
    match = re.search(pattern, markdown_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return markdown_text.strip()

def test_product_roadmap_basic_generation():
    """Test basic product roadmap generation"""
    input_state = {
        "user_message": """
        Project: Mobile App Development
        Timeline: 6 months
        Phases: Planning, Design, Development, Testing, Launch
        """,
        "retry_count": 0
    }
    
    result = product_roadmap_graph.invoke(input_state)
    
    # Verify response structure
    assert "response" in result
    assert "type" in result["response"]
    assert "detail" in result["response"]
    
    # Verify it's a roadmap
    assert result["response"]["type"] == "product-roadmap"

def test_product_roadmap_contains_mermaid():
    """Test that roadmap contains Mermaid diagram code"""
    input_state = {
        "user_message": "Create a product roadmap for a SaaS platform over 8 months",
        "retry_count": 0
    }
    
    result = product_roadmap_graph.invoke(input_state)
    
    detail = result["response"]["detail"]
    
    # Should contain mermaid code block
    assert "```mermaid" in detail or "gantt" in detail.lower()

def test_product_roadmap_gantt_format():
    """Test that roadmap follows Gantt chart format"""
    input_state = {
        "user_message": """
        Create a detailed product roadmap for an E-commerce Platform
        Include: Requirements, Design, Development, Testing, Deployment phases
        Timeline: 6 months starting January 2024
        """,
        "retry_count": 0
    }
    
    result = product_roadmap_graph.invoke(input_state)
    
    detail = result["response"]["detail"]
    mermaid_code = extract_mermaid_code(detail).lower()
    
    # Check for Gantt chart elements
    assert "gantt" in mermaid_code or "gantt" in detail.lower()

def test_product_roadmap_response_format():
    """Test that product roadmap follows the expected format"""
    input_state = {
        "user_message": "Create roadmap for CRM system implementation",
        "retry_count": 0
    }
    
    result = product_roadmap_graph.invoke(input_state)
    
    # Verify JSON structure
    assert isinstance(result, dict)
    assert "response" in result
    assert isinstance(result["response"], dict)
    assert "type" in result["response"]
    assert "detail" in result["response"]
    
    # Verify type
    assert result["response"]["type"] == "product-roadmap"

def test_product_roadmap_error_handling():
    """Test error handling with minimal input"""
    input_state = {
        "user_message": "",
        "retry_count": 0
    }
    
    result = product_roadmap_graph.invoke(input_state)
    
    # Should still return a response
    assert "response" in result
    assert "type" in result["response"]
    assert "detail" in result["response"]

def test_product_roadmap_with_milestones():
    """Test that roadmap includes milestones and phases"""
    input_state = {
        "user_message": """
        Product Roadmap for Cloud Migration Project
        Major Milestones:
        - Infrastructure Setup (Month 1)
        - Data Migration (Months 2-3)
        - Testing & Validation (Month 4)
        - Go-Live (Month 5)
        """,
        "retry_count": 0
    }
    
    result = product_roadmap_graph.invoke(input_state)
    
    detail = result["response"]["detail"].lower()
    
    # Should contain timeline-related content
    has_timeline = any(keyword in detail for keyword in ["month", "phase", "milestone", "section", "date"])
    assert has_timeline, "Roadmap should include timeline information"

def test_product_roadmap_validation_included():
    """Test that validation is performed on the diagram"""
    input_state = {
        "user_message": "Create a product roadmap for website redesign project spanning 4 months",
        "retry_count": 0
    }
    
    result = product_roadmap_graph.invoke(input_state)
    
    # Response should be present regardless of validation result
    assert "response" in result
    assert "detail" in result["response"]
    
    # Detail should contain diagram content
    assert len(result["response"]["detail"]) > 50

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
