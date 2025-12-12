# tests/test_business_planning_phase_integration.py
"""
Integration tests for Business Planning Phase workflows
Tests all three workflows: Business Case, Scope Statement, and Product Roadmap
"""
import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from workflows.business_case_workflow.workflow import business_case_graph
from workflows.scope_statement_workflow.workflow import scope_statement_graph
from workflows.product_roadmap_workflow.workflow import product_roadmap_graph

# Common test project data
TEST_PROJECT = {
    "name": "Enterprise Resource Planning System",
    "description": "Comprehensive ERP system to integrate all business processes",
    "investment": 2000000,
    "timeline": "18 months",
    "expected_benefits": [
        "40% improvement in operational efficiency",
        "25% cost reduction",
        "Real-time business insights"
    ]
}

class TestBusinessPlanningPhaseIntegration:
    """Integration tests for the complete Business Planning Phase"""
    
    def test_complete_business_planning_workflow(self):
        """Test all three workflows in sequence as they would be used in practice"""
        
        # Step 1: Generate Business Case
        business_case_input = {
            "user_message": f"""
            Project Name: {TEST_PROJECT['name']}
            Problem Statement: Current manual and disconnected business processes causing inefficiencies
            Proposed Solution: {TEST_PROJECT['description']}
            Estimated Investment: ${TEST_PROJECT['investment']}
            Expected Benefits: {', '.join(TEST_PROJECT['expected_benefits'])}
            Timeline: {TEST_PROJECT['timeline']}
            Strategic Alignment: Digital transformation, Operational excellence
            """
        }
        
        business_case_result = business_case_graph.invoke(business_case_input)
        
        # Verify business case
        assert "response" in business_case_result
        assert business_case_result["response"]["title"]
        assert business_case_result["response"]["content"]
        assert len(business_case_result["response"]["content"]) > 500
        
        # Step 2: Generate Scope Statement
        scope_statement_input = {
            "user_message": f"""
            Project Name: {TEST_PROJECT['name']}
            Project Description: {TEST_PROJECT['description']}
            Timeline: {TEST_PROJECT['timeline']}
            
            In Scope:
            - Financial management module
            - Inventory management module
            - HR management module
            - CRM integration
            - Reporting dashboard
            
            Out of Scope:
            - Third-party marketplace integrations
            - Mobile applications (Phase 2)
            
            Constraints:
            - Must integrate with existing database
            - Budget: ${TEST_PROJECT['investment']}
            - Must comply with GDPR and SOC2
            """
        }
        
        scope_statement_result = scope_statement_graph.invoke(scope_statement_input)
        
        # Verify scope statement
        assert "response" in scope_statement_result
        assert scope_statement_result["response"]["title"]
        assert scope_statement_result["response"]["content"]
        
        # Step 3: Generate Product Roadmap
        roadmap_input = {
            "user_message": f"""
            Project: {TEST_PROJECT['name']}
            Timeline: {TEST_PROJECT['timeline']}
            
            Major Phases:
            1. Requirements & Planning (Months 1-3)
            2. System Design & Architecture (Months 3-5)
            3. Financial Module Development (Months 5-8)
            4. Inventory Module Development (Months 8-11)
            5. HR Module Development (Months 11-14)
            6. Integration & Testing (Months 14-16)
            7. UAT & Training (Months 16-17)
            8. Deployment & Go-Live (Month 18)
            
            Key Milestones:
            - Requirements Sign-off: End of Month 3
            - Architecture Approval: End of Month 5
            - First Module Complete: End of Month 8
            - Integration Complete: End of Month 16
            - Go-Live: End of Month 18
            """,
            "retry_count": 0
        }
        
        roadmap_result = product_roadmap_graph.invoke(roadmap_input)
        
        # Verify product roadmap
        assert "response" in roadmap_result
        assert roadmap_result["response"]["type"] == "product-roadmap"
        assert roadmap_result["response"]["detail"]
        
        print("\n=== Business Planning Phase Integration Test Results ===")
        print(f"✓ Business Case generated: {len(business_case_result['response']['content'])} characters")
        print(f"✓ Scope Statement generated: {len(scope_statement_result['response']['content'])} characters")
        print(f"✓ Product Roadmap generated: {len(roadmap_result['response']['detail'])} characters")
        print("✓ All three workflows completed successfully")
    
    def test_business_case_workflow_standalone(self):
        """Test business case workflow independently"""
        input_state = {
            "user_message": f"""
            Generate a business case for {TEST_PROJECT['name']}
            Investment: ${TEST_PROJECT['investment']}
            Timeline: {TEST_PROJECT['timeline']}
            """
        }
        
        result = business_case_graph.invoke(input_state)
        
        assert "response" in result
        assert "title" in result["response"]
        assert "content" in result["response"]
        
        content_lower = result["response"]["content"].lower()
        # Verify key business case components
        assert any(term in content_lower for term in ["cost", "benefit", "roi", "investment"])
    
    def test_scope_statement_workflow_standalone(self):
        """Test scope statement workflow independently"""
        input_state = {
            "user_message": f"""
            Create a scope statement for {TEST_PROJECT['name']}
            Include clear in-scope and out-of-scope items
            """
        }
        
        result = scope_statement_graph.invoke(input_state)
        
        assert "response" in result
        assert "title" in result["response"]
        assert "content" in result["response"]
        
        content_lower = result["response"]["content"].lower()
        # Verify scope boundaries are defined
        assert "scope" in content_lower
    
    def test_product_roadmap_workflow_standalone(self):
        """Test product roadmap workflow independently"""
        input_state = {
            "user_message": f"""
            Create a product roadmap for {TEST_PROJECT['name']}
            Timeline: {TEST_PROJECT['timeline']}
            Show major phases and milestones
            """,
            "retry_count": 0
        }
        
        result = product_roadmap_graph.invoke(input_state)
        
        assert "response" in result
        assert result["response"]["type"] == "product-roadmap"
        assert result["response"]["detail"]
    
    def test_workflow_consistency(self):
        """Test that all workflows produce consistent project information"""
        project_input = f"""
        Project: {TEST_PROJECT['name']}
        Timeline: {TEST_PROJECT['timeline']}
        Budget: ${TEST_PROJECT['investment']}
        """
        
        # Generate all three documents
        bc_result = business_case_graph.invoke({"user_message": project_input})
        ss_result = scope_statement_graph.invoke({"user_message": project_input})
        pr_result = product_roadmap_graph.invoke({
            "user_message": project_input,
            "retry_count": 0
        })
        
        # All should produce non-empty results
        assert len(bc_result["response"]["content"]) > 0
        assert len(ss_result["response"]["content"]) > 0
        assert len(pr_result["response"]["detail"]) > 0
        
        print("\n=== Workflow Consistency Test ===")
        print("✓ All workflows generated content for the same project")
        print("✓ All responses are non-empty and structured correctly")
    
    def test_error_resilience(self):
        """Test that workflows handle errors gracefully"""
        
        # Test with minimal/empty input
        minimal_input = {"user_message": ""}
        
        bc_result = business_case_graph.invoke(minimal_input)
        ss_result = scope_statement_graph.invoke(minimal_input)
        pr_result = product_roadmap_graph.invoke({
            "user_message": "",
            "retry_count": 0
        })
        
        # All should still return valid structure even with empty input
        assert "response" in bc_result
        assert "response" in ss_result
        assert "response" in pr_result
        
        print("\n=== Error Resilience Test ===")
        print("✓ All workflows handled empty input gracefully")
        print("✓ All returned valid response structures")

def test_all_workflows_return_expected_types():
    """Test that all workflows return the correct response types"""
    test_message = "Create documentation for a test project"
    
    # Business Case should return markdown
    bc_result = business_case_graph.invoke({"user_message": test_message})
    assert "content" in bc_result["response"]
    assert isinstance(bc_result["response"]["content"], str)
    
    # Scope Statement should return markdown
    ss_result = scope_statement_graph.invoke({"user_message": test_message})
    assert "content" in ss_result["response"]
    assert isinstance(ss_result["response"]["content"], str)
    
    # Product Roadmap should return diagram
    pr_result = product_roadmap_graph.invoke({
        "user_message": test_message,
        "retry_count": 0
    })
    assert "detail" in pr_result["response"]
    assert isinstance(pr_result["response"]["detail"], str)
    assert pr_result["response"]["type"] == "product-roadmap"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
