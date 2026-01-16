"""
Integration tests for Legacy Wireframe Generation Workflow
Tests the wireframe_workflow that generates HTML/CSS wireframes
"""

import pytest
from workflows.wireframe_workflow import wireframe_graph


class TestLegacyWireframeWorkflow:
    """Integration tests for legacy wireframe workflow with HTML/CSS generation"""

    def test_wireframe_graph_available(self):
        """Test that wireframe graph is available"""
        assert wireframe_graph is not None, "Wireframe graph should be available"

    def test_wireframe_basic_generation(self):
        """Test basic wireframe generation with simple input"""
        state = {
            "user_message": "Create a login page wireframe",
            "content_id": None,
            "storage_paths": None
        }

        result = wireframe_graph.invoke(state)

        assert "response" in result
        assert isinstance(result["response"], dict)
        assert "content" in result["response"]
        assert len(result["response"]["content"]) > 0, "Should generate HTML/CSS content"

    def test_wireframe_with_detailed_requirements(self):
        """Test wireframe generation with detailed requirements"""
        state = {
            "user_message": "Generate wireframe for dashboard page with header, sidebar navigation, main content area, and footer",
            "content_id": None,
            "storage_paths": []
        }

        result = wireframe_graph.invoke(state)

        response = result["response"]
        assert response["content"], "Should have HTML/CSS content"
        assert isinstance(response["content"], str), "Content should be a string"

    def test_wireframe_mobile_responsive(self):
        """Test wireframe generation for mobile responsive design"""
        state = {
            "user_message": "Create responsive wireframe for e-commerce product listing page optimized for mobile and desktop",
            "content_id": None,
            "storage_paths": None
        }

        result = wireframe_graph.invoke(state)

        response = result["response"]
        assert "content" in response
        assert len(response["content"]) > 100, "Should generate substantial HTML/CSS"

    def test_wireframe_with_content_id(self):
        """Test wireframe workflow handles content_id parameter"""
        state = {
            "user_message": "Create wireframe for contact form",
            "content_id": "test-conversation-123",
            "storage_paths": None
        }

        result = wireframe_graph.invoke(state)
        assert "response" in result
        assert "content" in result["response"]

    def test_wireframe_with_storage_paths(self):
        """Test wireframe workflow handles storage_paths parameter"""
        state = {
            "user_message": "Generate wireframe for blog post layout",
            "content_id": None,
            "storage_paths": ["test-path-1.pdf", "test-path-2.pdf"]
        }

        result = wireframe_graph.invoke(state)
        assert "response" in result
        assert "content" in result["response"]

    def test_wireframe_complex_application(self):
        """Test wireframe generation for complex application"""
        state = {
            "user_message": "Create wireframe for admin panel with data tables, filters, charts, user management, and settings",
            "content_id": None,
            "storage_paths": []
        }

        result = wireframe_graph.invoke(state)

        response = result["response"]
        assert "content" in response, "Should have content field"
        assert isinstance(response["content"], str), "Content should be string"
        assert len(response["content"]) > 0, "Should generate non-empty content"

    def test_wireframe_different_page_types(self):
        """Test wireframe generation for different page types"""
        page_types = [
            "landing page with hero section and call-to-action",
            "user profile page with avatar and activity feed",
            "settings page with tabs and form inputs",
            "checkout page with order summary and payment form"
        ]

        for page_desc in page_types:
            state = {
                "user_message": f"Create wireframe for {page_desc}",
                "content_id": None,
                "storage_paths": None
            }

            result = wireframe_graph.invoke(state)
            assert "response" in result, f"Should generate response for {page_desc}"
            assert "content" in result["response"], f"Should have content for {page_desc}"

    def test_wireframe_with_extracted_text(self):
        """Test wireframe workflow with extracted text from documents"""
        state = {
            "user_message": "Create wireframe based on requirements",
            "content_id": None,
            "storage_paths": None,
            "extracted_text": "Requirements: The page should have a navigation bar, search functionality, and grid layout for products",
            "chat_context": None
        }

        result = wireframe_graph.invoke(state)
        assert "response" in result
        assert "content" in result["response"]

    def test_wireframe_with_chat_context(self):
        """Test wireframe workflow with chat history context"""
        state = {
            "user_message": "Generate the wireframe we discussed",
            "content_id": None,
            "storage_paths": None,
            "extracted_text": None,
            "chat_context": "User: I need a booking system\nAssistant: I can help create a wireframe for that"
        }

        result = wireframe_graph.invoke(state)
        assert "response" in result
        assert "content" in result["response"]

    def test_wireframe_error_handling(self):
        """Test wireframe workflow handles errors gracefully"""
        # Test with minimal input
        state = {
            "user_message": "",
            "content_id": None,
            "storage_paths": None
        }

        result = wireframe_graph.invoke(state)
        # Should still return a response structure even with empty message
        assert "response" in result
        assert isinstance(result["response"], dict)

    def test_wireframe_state_preservation(self):
        """Test that workflow preserves state fields"""
        state = {
            "user_message": "Create homepage wireframe",
            "content_id": "test-123",
            "storage_paths": ["path1.pdf"],
            "extracted_text": "Some context",
            "chat_context": "Previous chat"
        }

        result = wireframe_graph.invoke(state)
        
        # Response should be generated
        assert "response" in result
        # Original state fields should be preserved in result
        assert result.get("user_message") == "Create homepage wireframe"
