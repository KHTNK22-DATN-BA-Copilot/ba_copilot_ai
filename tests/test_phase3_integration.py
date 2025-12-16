# tests/test_phase3_integration.py
"""
Integration tests for Phase 3: Feasibility & Risk Analysis Phase
Tests all 4 new services together to ensure cohesive functionality
"""
import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflows.feasibility_study_workflow.workflow import feasibility_study_graph
from workflows.cost_benefit_analysis_workflow.workflow import cost_benefit_analysis_graph
from workflows.risk_register_workflow.workflow import risk_register_graph
from workflows.compliance_workflow.workflow import compliance_graph

class TestPhase3Integration:
    """Integration tests for all Phase 3 services"""
    
    @pytest.fixture
    def common_project_context(self):
        """Common project context for integration testing"""
        return {
            "user_message": """
            Project: Enterprise Resource Planning (ERP) System Implementation
            Industry: Manufacturing
            Budget: $5,000,000
            Timeline: 18 months
            Team Size: 30 people
            Geographic Scope: US and EU
            Technology Stack: Cloud-based, microservices architecture
            Regulatory Requirements: GDPR, SOX, ISO 27001
            Expected Benefits: 40% efficiency improvement, $2M annual cost savings
            Known Risks: Legacy system integration, change management, data migration
            """
        }
    
    def test_all_phase3_services_complete(self, common_project_context):
        """Test that all Phase 3 services can be invoked successfully"""
        
        # Test Feasibility Study
        feasibility_result = feasibility_study_graph.invoke(common_project_context)
        assert "response" in feasibility_result
        assert "title" in feasibility_result["response"]
        assert feasibility_result["response"]["title"]
        
        # Test Cost-Benefit Analysis
        cost_benefit_result = cost_benefit_analysis_graph.invoke(common_project_context)
        assert "response" in cost_benefit_result
        assert "title" in cost_benefit_result["response"]
        assert cost_benefit_result["response"]["title"]
        
        # Test Risk Register
        risk_result = risk_register_graph.invoke(common_project_context)
        assert "response" in risk_result
        assert "title" in risk_result["response"]
        assert risk_result["response"]["title"]
        
        # Test Compliance
        compliance_result = compliance_graph.invoke(common_project_context)
        assert "response" in compliance_result
        assert "title" in compliance_result["response"]
        assert compliance_result["response"]["title"]
    
    def test_phase3_services_consistency(self, common_project_context):
        """Test that all Phase 3 services return consistent structure"""
        
        services = [
            ("feasibility_study", feasibility_study_graph),
            ("cost_benefit_analysis", cost_benefit_analysis_graph),
            ("risk_register", risk_register_graph),
            ("compliance", compliance_graph)
        ]
        
        for service_name, graph in services:
            result = graph.invoke(common_project_context)
            
            # All should have response dict
            assert "response" in result, f"{service_name} missing response"
            assert isinstance(result["response"], dict), f"{service_name} response not dict"
            
            # All should have title
            assert "title" in result["response"], f"{service_name} missing title"
            
            # All should have executive_summary
            assert "executive_summary" in result["response"], f"{service_name} missing executive_summary"
            
            # All should have detail
            assert "detail" in result["response"], f"{service_name} missing detail"
            
            # Detail should have substantial content
            assert len(result["response"]["detail"]) > 100, f"{service_name} detail too short"
    
    def test_phase3_services_with_context(self):
        """Test Phase 3 services with chat context and file extractions"""
        
        input_with_context = {
            "user_message": "Create feasibility analysis for the discussed project",
            "content_id": None,
            "storage_paths": [],
            "extracted_text": "Previous analysis shows 60% stakeholder support",
            "chat_context": "We discussed implementing a new CRM system for sales team"
        }
        
        # Test each service handles context properly
        feasibility_result = feasibility_study_graph.invoke(input_with_context)
        assert feasibility_result["response"]["title"]
        
        cost_benefit_result = cost_benefit_analysis_graph.invoke(input_with_context)
        assert cost_benefit_result["response"]["title"]
        
        risk_result = risk_register_graph.invoke(input_with_context)
        assert risk_result["response"]["title"]
        
        compliance_result = compliance_graph.invoke(input_with_context)
        assert compliance_result["response"]["title"]
    
    def test_phase3_specific_fields_present(self):
        """Test that each Phase 3 service has its specific required fields"""
        
        base_input = {"user_message": "Analyze project for financial services platform"}
        
        # Feasibility Study specific fields
        feasibility = feasibility_study_graph.invoke(base_input)
        assert "technical_feasibility" in feasibility["response"]
        assert "operational_feasibility" in feasibility["response"]
        assert "economic_feasibility" in feasibility["response"]
        assert "schedule_feasibility" in feasibility["response"]
        assert "legal_feasibility" in feasibility["response"]
        
        # Cost-Benefit Analysis specific fields
        cost_benefit = cost_benefit_analysis_graph.invoke(base_input)
        assert "cost_analysis" in cost_benefit["response"]
        assert "benefit_analysis" in cost_benefit["response"]
        assert "roi_calculation" in cost_benefit["response"]
        assert "npv_analysis" in cost_benefit["response"]
        assert "payback_period" in cost_benefit["response"]
        
        # Risk Register specific fields
        risk = risk_register_graph.invoke(base_input)
        assert "risk_identification" in risk["response"]
        assert "risk_assessment" in risk["response"]
        assert "mitigation_strategies" in risk["response"]
        assert "contingency_plans" in risk["response"]
        
        # Compliance specific fields
        compliance = compliance_graph.invoke(base_input)
        assert "regulatory_requirements" in compliance["response"]
        assert "legal_requirements" in compliance["response"]
        assert "compliance_status" in compliance["response"]
        assert "recommendations" in compliance["response"]
    
    def test_phase3_error_handling(self):
        """Test that Phase 3 services handle errors gracefully"""
        
        # Empty message should still return valid structure
        empty_input = {"user_message": ""}
        
        for graph in [feasibility_study_graph, cost_benefit_analysis_graph, 
                     risk_register_graph, compliance_graph]:
            result = graph.invoke(empty_input)
            assert "response" in result
            assert "title" in result["response"]
    
    def test_phase3_sequential_workflow(self, common_project_context):
        """Test Phase 3 services in a typical sequential workflow"""
        
        # Step 1: Feasibility Study
        feasibility = feasibility_study_graph.invoke(common_project_context)
        assert feasibility["response"]["title"]
        feasibility_content = feasibility["response"]["detail"]
        
        # Step 2: Cost-Benefit Analysis (depends on feasibility findings)
        cost_benefit = cost_benefit_analysis_graph.invoke(common_project_context)
        assert cost_benefit["response"]["title"]
        cost_benefit_content = cost_benefit["response"]["detail"]
        
        # Step 3: Risk Register (identifies risks from feasibility/cost-benefit)
        risk = risk_register_graph.invoke(common_project_context)
        assert risk["response"]["title"]
        risk_content = risk["response"]["detail"]
        
        # Step 4: Compliance (addresses legal/regulatory concerns)
        compliance = compliance_graph.invoke(common_project_context)
        assert compliance["response"]["title"]
        compliance_content = compliance["response"]["detail"]
        
        # All documents should have substantial content
        assert all(len(content) > 200 for content in 
                  [feasibility_content, cost_benefit_content, risk_content, compliance_content])

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
