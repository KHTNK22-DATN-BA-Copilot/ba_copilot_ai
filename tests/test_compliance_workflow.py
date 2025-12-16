# tests/test_compliance_workflow.py
import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from workflows.compliance_workflow.workflow import compliance_graph

def test_compliance_basic_generation():
    """Test basic compliance document generation"""
    input_state = {
        "user_message": """
        Project: Healthcare Data Management System
        Compliance Requirements:
        - HIPAA compliance for patient data
        - SOC 2 Type II certification
        - Data encryption requirements
        Industry: Healthcare
        """
    }
    
    result = compliance_graph.invoke(input_state)
    
    # Verify response structure
    assert "response" in result
    assert "title" in result["response"]
    assert "executive_summary" in result["response"]
    assert "regulatory_requirements" in result["response"]
    assert "legal_requirements" in result["response"]
    assert "compliance_status" in result["response"]
    assert "recommendations" in result["response"]
    assert "detail" in result["response"]
    
    # Verify content has substance
    assert len(result["response"]["detail"]) > 100
    assert len(result["response"]["regulatory_requirements"]) > 0

def test_compliance_with_detailed_input():
    """Test compliance generation with comprehensive regulatory requirements"""
    input_state = {
        "user_message": """
        Project Name: E-commerce Payment Processing Platform
        Geographic Scope: US and EU operations
        Data Privacy: GDPR, CCPA compliance required
        Payment Security: PCI-DSS Level 1 compliance
        Accessibility: WCAG 2.1 AA standards
        Industry Standards: ISO 27001, SOC 2
        Legal Requirements: Consumer protection laws, data breach notification
        """
    }
    
    result = compliance_graph.invoke(input_state)
    
    # Verify response
    assert "response" in result
    assert result["response"]["title"]
    assert result["response"]["detail"]
    
    detail = result["response"]["detail"]
    # Check for key compliance sections
    assert any(keyword in detail.lower() for keyword in ["compliance", "regulatory", "legal", "standard"])

def test_compliance_response_format():
    """Test that compliance document follows the expected format"""
    input_state = {
        "user_message": "Create compliance document for financial trading platform requiring SEC and FINRA regulations"
    }
    
    result = compliance_graph.invoke(input_state)
    
    # Verify JSON structure
    assert isinstance(result, dict)
    assert "response" in result
    assert isinstance(result["response"], dict)
    
    # Verify all required fields
    required_fields = ["title", "executive_summary", "regulatory_requirements", 
                      "legal_requirements", "compliance_status", 
                      "recommendations", "detail"]
    for field in required_fields:
        assert field in result["response"]
        assert isinstance(result["response"][field], str)
        assert len(result["response"][field]) > 0

def test_compliance_contains_regulatory_terminology():
    """Test that generated document contains regulatory terminology"""
    input_state = {
        "user_message": "Analyze compliance requirements for IoT medical device software"
    }
    
    result = compliance_graph.invoke(input_state)
    
    detail = result["response"]["detail"].lower()
    
    # Should contain compliance keywords
    compliance_keywords = ["compliance", "regulation", "requirement", "standard", "legal"]
    assert any(keyword in detail for keyword in compliance_keywords)

def test_compliance_context_integration():
    """Test compliance generation with context"""
    input_state = {
        "user_message": "Document compliance requirements for data analytics platform",
        "content_id": None,
        "storage_paths": [],
        "extracted_text": "Platform processes personal data from EU citizens",
        "chat_context": ""
    }
    
    result = compliance_graph.invoke(input_state)
    
    assert "response" in result
    assert result["response"]["title"]
    assert "compliance" in result["response"]["title"].lower()

def test_compliance_multiple_jurisdictions():
    """Test compliance document covering multiple regulatory frameworks"""
    input_state = {
        "user_message": """
        Global SaaS platform compliance assessment covering:
        - GDPR (EU)
        - CCPA (California)
        - PIPEDA (Canada)
        - ISO 27001
        - SOC 2 Type II
        """
    }
    
    result = compliance_graph.invoke(input_state)
    
    # Should have comprehensive content
    assert len(result["response"]["regulatory_requirements"]) > 50
    assert len(result["response"]["recommendations"]) > 50

def test_compliance_industry_specific():
    """Test compliance for industry-specific regulations"""
    input_state = {
        "user_message": "Banking application compliance: PCI-DSS, GLBA, SOX, AML regulations"
    }
    
    result = compliance_graph.invoke(input_state)
    
    assert "response" in result
    assert result["response"]["regulatory_requirements"]
    assert result["response"]["legal_requirements"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
