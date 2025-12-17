# tests/test_cost_benefit_analysis_workflow.py
import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from workflows.cost_benefit_analysis_workflow.workflow import cost_benefit_analysis_graph

def test_cost_benefit_analysis_basic_generation():
    """Test basic cost-benefit analysis document generation"""
    input_state = {
        "user_message": """
        Project: CRM System Implementation
        Initial Cost: $300,000
        Annual Operating Cost: $50,000
        Expected Benefits: $150,000 annual revenue increase
        Project Duration: 3 years
        Discount Rate: 10%
        """
    }
    
    result = cost_benefit_analysis_graph.invoke(input_state)
    
    # Verify response structure
    assert "response" in result
    assert "title" in result["response"]
    assert "executive_summary" in result["response"]
    assert "cost_analysis" in result["response"]
    assert "benefit_analysis" in result["response"]
    assert "roi_calculation" in result["response"]
    assert "npv_analysis" in result["response"]
    assert "payback_period" in result["response"]
    assert "detail" in result["response"]
    
    # Verify content has substance
    assert len(result["response"]["detail"]) > 100
    assert len(result["response"]["cost_analysis"]) > 0

def test_cost_benefit_analysis_with_detailed_input():
    """Test cost-benefit analysis generation with comprehensive financial data"""
    input_state = {
        "user_message": """
        Project Name: Cloud Migration Initiative
        Initial Costs:
        - Infrastructure: $500,000
        - Migration services: $200,000
        - Training: $50,000
        Ongoing Costs: $100,000/year
        Expected Benefits:
        - Cost savings: $200,000/year
        - Productivity improvement: $150,000/year
        - Revenue increase: $100,000/year
        Timeline: 5 years
        Discount Rate: 8%
        """
    }
    
    result = cost_benefit_analysis_graph.invoke(input_state)
    
    # Verify response
    assert "response" in result
    assert result["response"]["title"]
    assert result["response"]["detail"]
    
    detail = result["response"]["detail"]
    # Check for key financial analysis sections
    assert any(keyword in detail.lower() for keyword in ["cost", "benefit", "roi", "npv", "payback"])

def test_cost_benefit_analysis_response_format():
    """Test that cost-benefit analysis follows the expected format"""
    input_state = {
        "user_message": "Analyze costs and benefits of implementing automated testing framework costing $100,000"
    }
    
    result = cost_benefit_analysis_graph.invoke(input_state)
    
    # Verify JSON structure
    assert isinstance(result, dict)
    assert "response" in result
    assert isinstance(result["response"], dict)
    
    # Verify all required fields
    required_fields = ["title", "executive_summary", "cost_analysis", 
                      "benefit_analysis", "roi_calculation", 
                      "npv_analysis", "payback_period", "detail"]
    for field in required_fields:
        assert field in result["response"]
        assert isinstance(result["response"][field], str)
        assert len(result["response"][field]) > 0

def test_cost_benefit_analysis_financial_keywords():
    """Test that generated analysis contains financial terminology"""
    input_state = {
        "user_message": "Conduct cost-benefit analysis for ERP system implementation, $2M investment"
    }
    
    result = cost_benefit_analysis_graph.invoke(input_state)
    
    detail = result["response"]["detail"].lower()
    
    # Should contain financial analysis keywords
    financial_keywords = ["cost", "benefit", "roi", "investment", "return"]
    assert any(keyword in detail for keyword in financial_keywords)

def test_cost_benefit_analysis_context_integration():
    """Test cost-benefit analysis generation with context"""
    input_state = {
        "user_message": "Analyze ROI for marketing automation platform",
        "content_id": None,
        "storage_paths": [],
        "extracted_text": "Current marketing team: 10 people. Manual process takes 40 hours/week",
        "chat_context": ""
    }
    
    result = cost_benefit_analysis_graph.invoke(input_state)
    
    assert "response" in result
    assert result["response"]["title"]
    assert "cost-benefit" in result["response"]["title"].lower() or "analysis" in result["response"]["title"].lower()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
