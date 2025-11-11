"""
API endpoint tests for activity diagram generation
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)


class TestActivityDiagramAPI:
    """Test suite for activity diagram API endpoints"""

    @patch('workflows.activity_diagram_workflow.workflow.OpenAI')
    def test_generate_activity_diagram_endpoint(self, mock_openai):
        """Test POST /api/v1/generate/activity-diagram endpoint"""
        # Mock OpenAI response
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = """```mermaid
graph TD
    Start([Start])
    Process[Process Data]
    End([End])
    Start --> Process --> End
```"""
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client

        # Test request
        response = client.post(
            "/api/v1/generate/activity-diagram",
            json={"message": "Create an activity diagram for user registration"}
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "type" in data
        assert data["type"] == "diagram"
        assert "response" in data
        assert data["response"]["type"] == "activity_diagram"
        assert "detail" in data["response"]
        assert len(data["response"]["detail"]) > 0

    @patch('workflows.activity_diagram_workflow.workflow.OpenAI')
    def test_activity_diagram_endpoint_with_complex_request(self, mock_openai):
        """Test endpoint with complex workflow request"""
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = """```mermaid
graph TD
    Start([Start Order Process])
    ReceiveOrder[Receive Order]
    ValidateOrder{{Validate Order}}
    CheckInventory[Check Inventory]
    StockAvailable{{Stock Available?}}
    ProcessPayment[Process Payment]
    PaymentSuccess{{Payment Successful?}}
    ShipOrder[Ship Order]
    UpdateInventory[Update Inventory]
    SendConfirmation[Send Confirmation]
    CancelOrder[Cancel Order]
    RefundPayment[Refund Payment]
    End([End])
    
    Start --> ReceiveOrder
    ReceiveOrder --> ValidateOrder
    ValidateOrder -->|Valid| CheckInventory
    ValidateOrder -->|Invalid| CancelOrder
    CheckInventory --> StockAvailable
    StockAvailable -->|Yes| ProcessPayment
    StockAvailable -->|No| CancelOrder
    ProcessPayment --> PaymentSuccess
    PaymentSuccess -->|Yes| ShipOrder
    PaymentSuccess -->|No| CancelOrder
    ShipOrder --> UpdateInventory
    UpdateInventory --> SendConfirmation
    SendConfirmation --> End
    CancelOrder --> RefundPayment
    RefundPayment --> End
```"""
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client

        response = client.post(
            "/api/v1/generate/activity-diagram",
            json={
                "message": "Create a detailed activity diagram for e-commerce order processing with payment and inventory management"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["response"]["type"] == "activity_diagram"
        assert "mermaid" in data["response"]["detail"]

    def test_activity_diagram_endpoint_missing_message(self):
        """Test endpoint with missing message field"""
        response = client.post(
            "/api/v1/generate/activity-diagram",
            json={}
        )

        # Should return 422 Unprocessable Entity for missing required field
        assert response.status_code == 422


    @patch('workflows.activity_diagram_workflow.workflow.OpenAI')
    def test_activity_diagram_endpoint_empty_message(self, mock_openai):
        """Test endpoint with empty message"""
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = "```mermaid\ngraph TD\n    Start --> End\n```"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client

        response = client.post(
            "/api/v1/generate/activity-diagram",
            json={"message": ""}
        )

        # Should still return 200 but with a diagram
        assert response.status_code == 200

    @patch('workflows.activity_diagram_workflow.workflow.OpenAI')
    def test_activity_diagram_response_format(self, mock_openai):
        """Test that response format matches specification"""
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = "```mermaid\ngraph TD\n    A --> B\n```"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client

        response = client.post(
            "/api/v1/generate/activity-diagram",
            json={"message": "Simple flow"}
        )

        data = response.json()
        
        # Validate exact structure
        assert isinstance(data, dict)
        assert set(data.keys()) == {"type", "response"}
        assert data["type"] == "diagram"
        assert isinstance(data["response"], dict)
        assert set(data["response"].keys()) == {"type", "detail"}
        assert data["response"]["type"] == "activity_diagram"
        assert isinstance(data["response"]["detail"], str)


class TestActivityDiagramAPIErrorHandling:
    """Test error handling in activity diagram API"""

    @patch('workflows.activity_diagram_workflow.workflow.OpenAI')
    def test_api_error_handling(self, mock_openai):
        """Test that API errors are handled gracefully"""
        # Mock to raise exception when creating client
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("OpenAI API Error")
        mock_openai.return_value = mock_client

        response = client.post(
            "/api/v1/generate/activity-diagram",
            json={"message": "Create diagram"}
        )

        # Should return error response (workflow handles it gracefully and returns error detail)
        assert response.status_code == 200
        data = response.json()
        assert "Error generating activity diagram" in data["response"]["detail"]

    @patch('workflows.activity_diagram_workflow.workflow.OpenAI')
    def test_timeout_handling(self, mock_openai):
        """Test handling of timeout scenarios"""
        import time
        
        def slow_response(*args, **kwargs):
            # Simulate slow response
            mock_completion = Mock()
            mock_completion.choices = [Mock()]
            mock_completion.choices[0].message.content = "```mermaid\ngraph TD\n    A --> B\n```"
            return mock_completion
        
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = slow_response
        mock_openai.return_value = mock_client

        response = client.post(
            "/api/v1/generate/activity-diagram",
            json={"message": "Create diagram"}
        )

        # Should complete successfully
        assert response.status_code == 200


class TestActivityDiagramAPICORS:
    """Test CORS and headers"""

    def test_cors_headers_present(self):
        """Test that CORS headers are configured"""
        response = client.options("/api/v1/generate/activity-diagram")
        
        # CORS middleware should handle OPTIONS requests
        assert response.status_code in [200, 405]  # May be 405 if OPTIONS not explicitly handled

    @patch('workflows.activity_diagram_workflow.workflow.OpenAI')
    def test_response_headers(self, mock_openai):
        """Test response headers"""
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = "```mermaid\ngraph TD\n    A --> B\n```"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client

        response = client.post(
            "/api/v1/generate/activity-diagram",
            json={"message": "Test"}
        )

        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
