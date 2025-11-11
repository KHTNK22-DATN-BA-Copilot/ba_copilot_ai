"""
Unit and integration tests for activity diagram generation workflow
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflows.activity_diagram_workflow import activity_diagram_graph
from models.diagram import DiagramResponse, DiagramOutput


class TestActivityDiagramWorkflow:
    """Test suite for activity diagram workflow"""

    def test_activity_diagram_graph_exists(self):
        """Test that activity_diagram_graph is properly exported"""
        assert activity_diagram_graph is not None

    @patch('workflows.activity_diagram_workflow.workflow.OpenAI')
    def test_generate_activity_diagram_success(self, mock_openai):
        """Test successful activity diagram generation"""
        # Mock the OpenAI response
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = """```mermaid
graph TD
    Start([Start])
    ValidateInput[Validate User Input]
    Decision{{Valid?}}
    ProcessData[Process Data]
    SaveDB[Save to Database]
    SendNotification[Send Notification]
    Error[Show Error]
    End([End])
    
    Start --> ValidateInput
    ValidateInput --> Decision
    Decision -->|Yes| ProcessData
    Decision -->|No| Error
    ProcessData --> SaveDB
    SaveDB --> SendNotification
    SendNotification --> End
    Error --> End
```"""
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client

        # Test input
        test_input = {
            "user_message": "Create an activity diagram for user registration process"
        }

        # Invoke workflow
        result = activity_diagram_graph.invoke(test_input)

        # Assertions
        assert result is not None
        assert "response" in result
        assert result["response"]["type"] == "activity_diagram"
        assert "detail" in result["response"]
        assert "mermaid" in result["response"]["detail"]
        assert "graph TD" in result["response"]["detail"] or "flowchart" in result["response"]["detail"]

    @patch('workflows.activity_diagram_workflow.workflow.OpenAI')
    def test_generate_activity_diagram_with_complex_flow(self, mock_openai):
        """Test activity diagram generation with complex workflow"""
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = """```mermaid
graph TD
    Start([Start])
    Login[User Login]
    Auth{{Authenticated?}}
    SelectProduct[Select Product]
    AddCart[Add to Cart]
    Checkout{{Checkout?}}
    ProcessPayment[Process Payment]
    PaymentSuccess{{Payment Success?}}
    GenerateInvoice[Generate Invoice]
    SendEmail[Send Confirmation Email]
    UpdateInventory[Update Inventory]
    End([End])
    Logout[Logout]
    
    Start --> Login
    Login --> Auth
    Auth -->|Yes| SelectProduct
    Auth -->|No| Login
    SelectProduct --> AddCart
    AddCart --> Checkout
    Checkout -->|Yes| ProcessPayment
    Checkout -->|No| SelectProduct
    ProcessPayment --> PaymentSuccess
    PaymentSuccess -->|Yes| GenerateInvoice
    PaymentSuccess -->|No| AddCart
    GenerateInvoice --> SendEmail
    SendEmail --> UpdateInventory
    UpdateInventory --> End
    SelectProduct --> Logout
    Logout --> End
```"""
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client

        test_input = {
            "user_message": "Create an activity diagram for e-commerce checkout process"
        }

        result = activity_diagram_graph.invoke(test_input)

        assert result is not None
        assert result["response"]["type"] == "activity_diagram"
        assert "graph TD" in result["response"]["detail"] or "flowchart" in result["response"]["detail"]

    @patch('workflows.activity_diagram_workflow.workflow.OpenAI')
    def test_generate_activity_diagram_error_handling(self, mock_openai):
        """Test error handling when API call fails"""
        # Mock the OpenAI client to raise an exception during completion
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API connection failed")
        mock_openai.return_value = mock_client

        test_input = {
            "user_message": "Create an activity diagram"
        }

        result = activity_diagram_graph.invoke(test_input)

        assert result is not None
        assert "response" in result
        assert result["response"]["type"] == "activity_diagram"
        assert "Error generating activity diagram" in result["response"]["detail"]

    @patch('workflows.activity_diagram_workflow.workflow.OpenAI')
    def test_activity_diagram_contains_key_elements(self, mock_openai):
        """Test that generated diagram contains key activity diagram elements"""
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = """```mermaid
graph TD
    Start([Start])
    Activity1[Process Request]
    Decision{{Is Valid?}}
    Activity2[Execute Action]
    End([End])
    
    Start --> Activity1
    Activity1 --> Decision
    Decision -->|Yes| Activity2
    Decision -->|No| End
    Activity2 --> End
```"""
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client

        test_input = {
            "user_message": "Simple activity diagram"
        }

        result = activity_diagram_graph.invoke(test_input)
        detail = result["response"]["detail"]

        # Check for common activity diagram elements
        assert "Start" in detail or "start" in detail.lower()
        assert "End" in detail or "end" in detail.lower()
        assert "-->" in detail or "--->" in detail  # Flow arrows

    @patch('workflows.activity_diagram_workflow.workflow.OpenAI')
    def test_activity_diagram_response_structure(self, mock_openai):
        """Test that response follows correct structure"""
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = "```mermaid\ngraph TD\n    Start([Start])\n    End([End])\n    Start --> End\n```"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client

        test_input = {
            "user_message": "Simple flow"
        }

        result = activity_diagram_graph.invoke(test_input)

        # Validate response structure
        assert isinstance(result, dict)
        assert "response" in result
        assert isinstance(result["response"], dict)
        assert "type" in result["response"]
        assert "detail" in result["response"]
        assert isinstance(result["response"]["type"], str)
        assert isinstance(result["response"]["detail"], str)

    def test_activity_diagram_state_type(self):
        """Test that ActivityDiagramState is properly defined"""
        from workflows.activity_diagram_workflow.workflow import ActivityDiagramState
        
        # Create a valid state
        state = {
            "user_message": "test message",
            "response": {}
        }
        
        # This should not raise any errors
        assert "user_message" in state
        assert "response" in state


class TestActivityDiagramIntegration:
    """Integration tests for activity diagram endpoint"""

    @pytest.fixture
    def test_message(self):
        """Fixture for test message"""
        return "Create an activity diagram for a library management system with book checkout and return processes"

    @patch('workflows.activity_diagram_workflow.workflow.OpenAI')
    def test_end_to_end_activity_diagram_generation(self, mock_openai, test_message):
        """Test complete workflow from input to output"""
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = """```mermaid
graph TD
    Start([Start])
    SearchBook[Search for Book]
    BookAvailable{{Book Available?}}
    CheckoutBook[Checkout Book]
    UpdateRecord[Update Library Record]
    GenerateReceipt[Generate Receipt]
    ReturnBook[Return Book]
    CheckCondition{{Book Condition OK?}}
    AcceptReturn[Accept Return]
    ChargeFee[Charge Penalty Fee]
    End([End])
    
    Start --> SearchBook
    SearchBook --> BookAvailable
    BookAvailable -->|Yes| CheckoutBook
    BookAvailable -->|No| End
    CheckoutBook --> UpdateRecord
    UpdateRecord --> GenerateReceipt
    GenerateReceipt --> ReturnBook
    ReturnBook --> CheckCondition
    CheckCondition -->|Yes| AcceptReturn
    CheckCondition -->|No| ChargeFee
    AcceptReturn --> End
    ChargeFee --> End
```"""
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client

        result = activity_diagram_graph.invoke({"user_message": test_message})

        # Comprehensive assertions
        assert result is not None
        assert "response" in result
        assert result["response"]["type"] == "activity_diagram"
        assert len(result["response"]["detail"]) > 0
        assert "mermaid" in result["response"]["detail"]

    @patch('workflows.activity_diagram_workflow.workflow.OpenAI')
    def test_multiple_diagram_generations(self, mock_openai):
        """Test generating multiple diagrams in sequence"""
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = "```mermaid\ngraph TD\n    A --> B\n```"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client

        messages = [
            "User login process",
            "Payment processing workflow",
            "Order fulfillment activity"
        ]

        results = []
        for msg in messages:
            result = activity_diagram_graph.invoke({"user_message": msg})
            results.append(result)

        # All should succeed
        assert len(results) == 3
        for result in results:
            assert result["response"]["type"] == "activity_diagram"
            assert "detail" in result["response"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
