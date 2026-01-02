"""
Integration tests for Phase 6: UI/UX Design Phase
Tests wireframe, mockup, and prototype generation workflows
"""

import pytest
from workflows.uiux_wireframe_workflow import uiux_wireframe_graph
from workflows.uiux_mockup_workflow import uiux_mockup_graph
from workflows.uiux_prototype_workflow import uiux_prototype_graph


class TestPhase6Integration:
    """Integration tests for Phase 6 UI/UX Design workflows"""

    def test_all_phase6_workflows_available(self):
        """Test that all Phase 6 workflow graphs are available"""
        assert uiux_wireframe_graph is not None, "Wireframe graph should be available"
        assert uiux_mockup_graph is not None, "Mockup graph should be available"
        assert uiux_prototype_graph is not None, "Prototype graph should be available"

    def test_wireframe_workflow_basic(self):
        """Test wireframe workflow with basic input"""
        state = {
            "message": "Create wireframe for login page",
            "content_id": None,
            "storage_paths": None
        }

        result = uiux_wireframe_graph.invoke(state)

        assert "response" in result
        assert isinstance(result["response"], dict)
        assert "title" in result["response"]
        assert "wireframe_type" in result["response"]
        assert "detail" in result["response"]

    def test_mockup_workflow_basic(self):
        """Test mockup workflow with basic input"""
        state = {
            "message": "Create mockup for dashboard page",
            "content_id": None,
            "storage_paths": None
        }

        result = uiux_mockup_graph.invoke(state)

        assert "response" in result
        assert isinstance(result["response"], dict)
        assert "title" in result["response"]
        assert "mockup_type" in result["response"]
        assert "color_palette" in result["response"]
        assert "typography" in result["response"]

    def test_prototype_workflow_basic(self):
        """Test prototype workflow with basic input"""
        state = {
            "message": "Create prototype for e-commerce checkout flow",
            "content_id": None,
            "storage_paths": None
        }

        result = uiux_prototype_graph.invoke(state)

        assert "response" in result
        assert isinstance(result["response"], dict)
        assert "title" in result["response"]
        assert "prototype_type" in result["response"]
        assert "user_flows" in result["response"]
        assert "interactions" in result["response"]

    def test_wireframe_complete_workflow(self):
        """Test complete wireframe generation with detailed requirements"""
        state = {
            "message": "Generate wireframe for mobile app home screen with navigation, search bar, and product grid",
            "content_id": None,
            "storage_paths": []
        }

        result = uiux_wireframe_graph.invoke(state)

        response = result["response"]
        assert response["title"], "Wireframe should have a title"
        assert response["wireframe_type"] in ["low-fidelity", "high-fidelity", "interactive"], \
            "Wireframe type should be one of the expected types"
        assert len(response["screens"]) > 0, "Should specify screens"
        assert len(response["layout_structure"]) > 0, "Should specify layout structure"
        assert len(response["components"]) > 0, "Should list UI components"

    def test_mockup_complete_workflow(self):
        """Test complete mockup generation with design system"""
        state = {
            "message": "Generate high-fidelity mockup for SaaS dashboard with modern design system",
            "content_id": None,
            "storage_paths": []
        }

        result = uiux_mockup_graph.invoke(state)

        response = result["response"]
        assert response["title"], "Mockup should have a title"
        assert response["mockup_type"] in ["visual-design", "high-fidelity", "pixel-perfect"], \
            "Mockup type should be one of the expected types"
        assert len(response["design_system"]) > 0, "Should specify design system"
        assert len(response["color_palette"]) > 0, "Should include color palette"
        assert len(response["typography"]) > 0, "Should include typography specs"

    def test_prototype_complete_workflow(self):
        """Test complete prototype generation with interactions"""
        state = {
            "message": "Generate interactive prototype for user registration and onboarding flow",
            "content_id": None,
            "storage_paths": []
        }

        result = uiux_prototype_graph.invoke(state)

        response = result["response"]
        assert response["title"], "Prototype should have a title"
        # Check if prototype_type contains any of the expected keywords (LLM may return combined values)
        valid_types = ["interactive", "clickable", "animated"]
        prototype_type = response["prototype_type"].lower()
        assert any(vt in prototype_type for vt in valid_types), \
            f"Prototype type '{prototype_type}' should contain one of: {valid_types}"
        assert len(response["user_flows"]) > 0, "Should specify user flows"
        assert len(response["interactions"]) > 0, "Should define interactions"
        assert len(response["states"]) > 0, "Should include UI states"

    def test_wireframe_handles_content_id(self):
        """Test wireframe workflow handles content_id gracefully"""
        state = {
            "message": "Create wireframe for product page",
            "content_id": "test-conversation-id",
            "storage_paths": None
        }

        result = uiux_wireframe_graph.invoke(state)
        assert "response" in result
        assert result["response"]["title"], "Should generate wireframe even with content_id"

    def test_mockup_handles_storage_paths(self):
        """Test mockup workflow handles storage_paths gracefully"""
        state = {
            "message": "Create mockup for landing page",
            "content_id": None,
            "storage_paths": ["non-existent-path.pdf"]
        }

        result = uiux_mockup_graph.invoke(state)
        assert "response" in result
        assert result["response"]["title"], "Should generate mockup even with invalid storage paths"

    def test_phase6_response_completeness(self):
        """Test that all Phase 6 workflows return complete responses"""
        test_message = "Create UI for blog platform"

        # Test wireframe
        wireframe_result = uiux_wireframe_graph.invoke({"message": test_message})
        wireframe_response = wireframe_result["response"]
        assert all(key in wireframe_response for key in [
            "title", "wireframe_type", "screens", "layout_structure",
            "components", "navigation_flow", "annotations", "responsive_behavior", "detail"
        ]), "Wireframe response should have all required fields"

        # Test mockup
        mockup_result = uiux_mockup_graph.invoke({"message": test_message})
        mockup_response = mockup_result["response"]
        assert all(key in mockup_response for key in [
            "title", "mockup_type", "design_system", "visual_hierarchy",
            "color_palette", "typography", "iconography", "imagery_style", "ui_elements", "detail"
        ]), "Mockup response should have all required fields"

        # Test prototype
        prototype_result = uiux_prototype_graph.invoke({"message": test_message})
        prototype_response = prototype_result["response"]
        assert all(key in prototype_response for key in [
            "title", "prototype_type", "user_flows", "interactions",
            "animations", "states", "scenarios", "accessibility", "testing_notes", "detail"
        ]), "Prototype response should have all required fields"

    def test_wireframe_responsive_design(self):
        """Test wireframe includes responsive design considerations"""
        state = {
            "message": "Generate responsive wireframe for e-commerce product listing",
            "content_id": None,
            "storage_paths": []
        }

        result = uiux_wireframe_graph.invoke(state)
        response = result["response"]

        assert "responsive_behavior" in response
        assert len(response["responsive_behavior"]) > 0, \
            "Should include responsive behavior specifications"

    def test_mockup_design_system(self):
        """Test mockup includes comprehensive design system"""
        state = {
            "message": "Create design system mockup for corporate website",
            "content_id": None,
            "storage_paths": []
        }

        result = uiux_mockup_graph.invoke(state)
        response = result["response"]

        # Verify design system components
        assert "design_system" in response and len(response["design_system"]) > 0
        assert "color_palette" in response and len(response["color_palette"]) > 0
        assert "typography" in response and len(response["typography"]) > 0
        assert "iconography" in response

    def test_prototype_accessibility(self):
        """Test prototype includes accessibility features"""
        state = {
            "message": "Generate accessible prototype for healthcare portal",
            "content_id": None,
            "storage_paths": []
        }

        result = uiux_prototype_graph.invoke(state)
        response = result["response"]

        assert "accessibility" in response
        assert len(response["accessibility"]) > 0, \
            "Should include accessibility specifications"

    def test_all_phase6_workflows_execute(self):
        """Test that all Phase 6 workflows can execute successfully"""
        test_message = "Design UI/UX for social media app"

        workflows = [
            ("wireframe", uiux_wireframe_graph),
            ("mockup", uiux_mockup_graph),
            ("prototype", uiux_prototype_graph)
        ]

        for name, workflow in workflows:
            state = {"message": test_message, "content_id": None, "storage_paths": []}
            result = workflow.invoke(state)

            assert "response" in result, f"{name} workflow should return response"
            assert isinstance(result["response"], dict), f"{name} response should be a dict"
            assert "title" in result["response"], f"{name} should have a title"
            assert "detail" in result["response"], f"{name} should have detail field"
