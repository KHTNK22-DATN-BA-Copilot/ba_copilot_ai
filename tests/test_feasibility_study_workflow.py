# tests/test_feasibility_study_workflow.py
import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from workflows.feasibility_study_workflow.workflow import feasibility_study_graph

def test_feasibility_study_basic_generation():
    """Test basic feasibility study document generation"""
    input_state = {
        "user_message": """
        Project: E-commerce Platform Development
        Technology: Python/Django, React, PostgreSQL
        Team: 5 developers available
        Budget: $500,000
        Timeline: 6 months
        Regulatory: GDPR compliance required
        """
    }
    
    result = feasibility_study_graph.invoke(input_state)
    
    # Verify response structure
    assert "response" in result
    assert "title" in result["response"]
    assert "executive_summary" in result["response"]
    assert "technical_feasibility" in result["response"]
    assert "operational_feasibility" in result["response"]
    assert "economic_feasibility" in result["response"]
    assert "schedule_feasibility" in result["response"]
    assert "legal_feasibility" in result["response"]
    assert "detail" in result["response"]
    
    # Verify content has substance
    assert len(result["response"]["detail"]) > 100
    assert len(result["response"]["technical_feasibility"]) > 0

def test_feasibility_study_with_detailed_input():
    """Test feasibility study generation with comprehensive requirements"""
    input_state = {
        "user_message": """
        Project Name: Healthcare Management System
        Technical Requirements: Cloud-based, HIPAA compliant, HL7 integration
        Operational Requirements: 24/7 availability, support for 1000+ concurrent users
        Budget: $1,000,000
        Timeline: 12 months
        Team Availability: Experienced healthcare IT team
        Legal Requirements: HIPAA, FDA regulations
        """
    }
    
    result = feasibility_study_graph.invoke(input_state)
    
    # Verify response
    assert "response" in result
    assert result["response"]["title"]
    assert result["response"]["detail"]
    
    detail = result["response"]["detail"]
    # Check for key feasibility study sections
    assert any(keyword in detail.lower() for keyword in ["technical", "operational", "economic", "legal"])

def test_feasibility_study_response_format():
    """Test that feasibility study follows the expected format"""
    input_state = {
        "user_message": "Analyze feasibility of implementing AI chatbot for customer support"
    }
    
    result = feasibility_study_graph.invoke(input_state)
    
    # Verify JSON structure
    assert isinstance(result, dict)
    assert "response" in result
    assert isinstance(result["response"], dict)
    
    # Verify all required fields
    required_fields = ["title", "executive_summary", "technical_feasibility", 
                      "operational_feasibility", "economic_feasibility", 
                      "schedule_feasibility", "legal_feasibility", "detail"]
    for field in required_fields:
        assert field in result["response"]
        assert isinstance(result["response"][field], str)
        assert len(result["response"][field]) > 0

def test_feasibility_study_context_integration():
    """Test feasibility study generation with context"""
    input_state = {
        "user_message": "Assess feasibility of blockchain-based supply chain system",
        "content_id": None,
        "storage_paths": [],
        "extracted_text": "",
        "chat_context": "Previous discussion about improving supply chain transparency"
    }
    
    result = feasibility_study_graph.invoke(input_state)
    
    assert "response" in result
    assert result["response"]["title"]
    assert "feasibility" in result["response"]["title"].lower()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
