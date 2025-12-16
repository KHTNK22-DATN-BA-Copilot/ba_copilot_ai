# tests/test_risk_register_workflow.py
import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from workflows.risk_register_workflow.workflow import risk_register_graph

def test_risk_register_basic_generation():
    """Test basic risk register document generation"""
    input_state = {
        "user_message": """
        Project: Mobile App Development
        Known Risks:
        - Technical: Integration with legacy systems
        - Operational: Limited experienced mobile developers
        - Financial: Budget constraints
        - External: Market competition
        """
    }
    
    result = risk_register_graph.invoke(input_state)
    
    # Verify response structure
    assert "response" in result
    assert "title" in result["response"]
    assert "executive_summary" in result["response"]
    assert "risk_identification" in result["response"]
    assert "risk_assessment" in result["response"]
    assert "mitigation_strategies" in result["response"]
    assert "contingency_plans" in result["response"]
    assert "detail" in result["response"]
    
    # Verify content has substance
    assert len(result["response"]["detail"]) > 100
    assert len(result["response"]["risk_identification"]) > 0

def test_risk_register_with_detailed_input():
    """Test risk register generation with comprehensive risk scenarios"""
    input_state = {
        "user_message": """
        Project Name: Cloud Infrastructure Migration
        Technical Risks: Data migration complexity, system downtime, integration issues
        Operational Risks: Staff training needs, change management resistance
        Financial Risks: Budget overruns, hidden costs
        Security Risks: Data breaches, compliance violations
        External Risks: Vendor reliability, market changes
        Project Timeline: 12 months
        Budget: $2,000,000
        """
    }
    
    result = risk_register_graph.invoke(input_state)
    
    # Verify response
    assert "response" in result
    assert result["response"]["title"]
    assert result["response"]["detail"]
    
    detail = result["response"]["detail"]
    # Check for key risk management sections
    assert any(keyword in detail.lower() for keyword in ["risk", "mitigation", "probability", "impact"])

def test_risk_register_response_format():
    """Test that risk register follows the expected format"""
    input_state = {
        "user_message": "Create a risk register for implementing a new payment gateway system"
    }
    
    result = risk_register_graph.invoke(input_state)
    
    # Verify JSON structure
    assert isinstance(result, dict)
    assert "response" in result
    assert isinstance(result["response"], dict)
    
    # Verify all required fields
    required_fields = ["title", "executive_summary", "risk_identification", 
                      "risk_assessment", "mitigation_strategies", 
                      "contingency_plans", "detail"]
    for field in required_fields:
        assert field in result["response"]
        assert isinstance(result["response"][field], str)
        assert len(result["response"][field]) > 0

def test_risk_register_contains_risk_terminology():
    """Test that generated register contains risk management terminology"""
    input_state = {
        "user_message": "Identify risks for AI model deployment in production environment"
    }
    
    result = risk_register_graph.invoke(input_state)
    
    detail = result["response"]["detail"].lower()
    
    # Should contain risk management keywords
    risk_keywords = ["risk", "probability", "impact", "mitigation", "contingency"]
    assert any(keyword in detail for keyword in risk_keywords)

def test_risk_register_context_integration():
    """Test risk register generation with context"""
    input_state = {
        "user_message": "Create risk register for blockchain implementation",
        "content_id": None,
        "storage_paths": [],
        "extracted_text": "",
        "chat_context": "Project involves cryptocurrency transactions and regulatory compliance"
    }
    
    result = risk_register_graph.invoke(input_state)
    
    assert "response" in result
    assert result["response"]["title"]
    assert "risk" in result["response"]["title"].lower()

def test_risk_register_multiple_risk_categories():
    """Test that risk register covers multiple risk categories"""
    input_state = {
        "user_message": """
        Identify all risks for enterprise software rollout including:
        technical, operational, financial, legal, and reputational risks
        """
    }
    
    result = risk_register_graph.invoke(input_state)
    
    # Should have comprehensive content
    assert len(result["response"]["risk_identification"]) > 50
    assert len(result["response"]["mitigation_strategies"]) > 50

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
