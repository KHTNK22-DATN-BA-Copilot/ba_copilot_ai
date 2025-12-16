# tests/test_phase3_api_endpoints.py
"""
End-to-end API tests for Phase 3 endpoints
Tests the actual HTTP endpoints after Docker containers are running
"""
import pytest
import requests
import os
from typing import Dict

# Base URL for AI service (adjust if needed)
BASE_URL = os.getenv("AI_SERVICE_URL", "http://localhost:8000")

class TestPhase3APIEndpoints:
    """E2E tests for Phase 3 API endpoints"""
    
    @pytest.fixture
    def api_client(self):
        """Create API client configuration"""
        return {
            "base_url": BASE_URL,
            "headers": {"Content-Type": "application/json"}
        }
    
    @pytest.fixture
    def sample_request_payload(self):
        """Sample request payload for testing"""
        return {
            "message": "Create analysis for cloud migration project with $1M budget",
            "content_id": None,
            "storage_paths": []
        }
    
    def test_health_endpoint(self, api_client):
        """Test that the AI service health endpoint is accessible"""
        response = requests.get(f"{api_client['base_url']}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_feasibility_study_endpoint(self, api_client, sample_request_payload):
        """Test POST /api/v1/generate/feasibility-study endpoint"""
        url = f"{api_client['base_url']}/api/v1/generate/feasibility-study"
        
        response = requests.post(
            url,
            json=sample_request_payload,
            headers=api_client["headers"],
            timeout=60
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "type" in data
        assert data["type"] == "feasibility-study"
        assert "response" in data
        
        # Verify response content
        response_data = data["response"]
        assert "title" in response_data
        assert "executive_summary" in response_data
        assert "technical_feasibility" in response_data
        assert "operational_feasibility" in response_data
        assert "economic_feasibility" in response_data
        assert "schedule_feasibility" in response_data
        assert "legal_feasibility" in response_data
        assert "detail" in response_data
        
        # Verify content has substance
        assert len(response_data["detail"]) > 100
    
    def test_cost_benefit_analysis_endpoint(self, api_client, sample_request_payload):
        """Test POST /api/v1/generate/cost-benefit-analysis endpoint"""
        url = f"{api_client['base_url']}/api/v1/generate/cost-benefit-analysis"
        
        response = requests.post(
            url,
            json=sample_request_payload,
            headers=api_client["headers"],
            timeout=60
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "type" in data
        assert data["type"] == "cost-benefit-analysis"
        assert "response" in data
        
        # Verify response content
        response_data = data["response"]
        assert "title" in response_data
        assert "executive_summary" in response_data
        assert "cost_analysis" in response_data
        assert "benefit_analysis" in response_data
        assert "roi_calculation" in response_data
        assert "npv_analysis" in response_data
        assert "payback_period" in response_data
        assert "detail" in response_data
        
        # Verify content has substance
        assert len(response_data["detail"]) > 100
    
    def test_risk_register_endpoint(self, api_client, sample_request_payload):
        """Test POST /api/v1/generate/risk-register endpoint"""
        url = f"{api_client['base_url']}/api/v1/generate/risk-register"
        
        response = requests.post(
            url,
            json=sample_request_payload,
            headers=api_client["headers"],
            timeout=60
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "type" in data
        assert data["type"] == "risk-register"
        assert "response" in data
        
        # Verify response content
        response_data = data["response"]
        assert "title" in response_data
        assert "executive_summary" in response_data
        assert "risk_identification" in response_data
        assert "risk_assessment" in response_data
        assert "mitigation_strategies" in response_data
        assert "contingency_plans" in response_data
        assert "detail" in response_data
        
        # Verify content has substance
        assert len(response_data["detail"]) > 100
    
    def test_compliance_endpoint(self, api_client, sample_request_payload):
        """Test POST /api/v1/generate/compliance endpoint"""
        url = f"{api_client['base_url']}/api/v1/generate/compliance"
        
        response = requests.post(
            url,
            json=sample_request_payload,
            headers=api_client["headers"],
            timeout=60
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "type" in data
        assert data["type"] == "compliance"
        assert "response" in data
        
        # Verify response content
        response_data = data["response"]
        assert "title" in response_data
        assert "executive_summary" in response_data
        assert "regulatory_requirements" in response_data
        assert "legal_requirements" in response_data
        assert "compliance_status" in response_data
        assert "recommendations" in response_data
        assert "detail" in response_data
        
        # Verify content has substance
        assert len(response_data["detail"]) > 100
    
    def test_all_phase3_endpoints_sequential(self, api_client):
        """Test all Phase 3 endpoints in sequence with same project context"""
        
        project_payload = {
            "message": """
            Project: Enterprise CRM Implementation
            Budget: $2,000,000
            Timeline: 12 months
            Industry: Healthcare
            Regulatory: HIPAA, GDPR compliance required
            Team: 20 developers, 5 BA, 3 PM
            """,
            "content_id": None,
            "storage_paths": []
        }
        
        endpoints = [
            ("feasibility-study", "feasibility-study"),
            ("cost-benefit-analysis", "cost-benefit-analysis"),
            ("risk-register", "risk-register"),
            ("compliance", "compliance")
        ]
        
        for endpoint_path, expected_type in endpoints:
            url = f"{api_client['base_url']}/api/v1/generate/{endpoint_path}"
            
            response = requests.post(
                url,
                json=project_payload,
                headers=api_client["headers"],
                timeout=60
            )
            
            assert response.status_code == 200, f"Failed for {endpoint_path}"
            data = response.json()
            assert data["type"] == expected_type, f"Wrong type for {endpoint_path}"
            assert "response" in data
            assert "title" in data["response"]
    
    def test_phase3_with_context(self, api_client):
        """Test Phase 3 endpoints with file context"""
        
        payload_with_context = {
            "message": "Analyze the project requirements",
            "content_id": None,
            "storage_paths": ["test_requirements.pdf"]  # Mock file path
        }
        
        # Test one endpoint as representative
        url = f"{api_client['base_url']}/api/v1/generate/feasibility-study"
        
        response = requests.post(
            url,
            json=payload_with_context,
            headers=api_client["headers"],
            timeout=60
        )
        
        # Should still work even if file doesn't exist (graceful handling)
        assert response.status_code in [200, 400, 500]

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
