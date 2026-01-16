"""
Integration tests for LLD (Low-Level Design) Phase Workflows
Tests lld-api, lld-db, lld-arch, and lld-pseudo generation workflows
"""

import pytest
from workflows.lld_api_workflow import lld_api_graph
from workflows.lld_db_workflow import lld_db_graph
from workflows.lld_arch_workflow import lld_arch_graph
from workflows.lld_pseudo_workflow import lld_pseudo_graph


class TestLLDWorkflows:
    """Integration tests for all LLD workflow graphs"""

    def test_all_lld_workflows_available(self):
        """Test that all LLD workflow graphs are available"""
        assert lld_api_graph is not None, "LLD API graph should be available"
        assert lld_db_graph is not None, "LLD Database graph should be available"
        assert lld_arch_graph is not None, "LLD Architecture graph should be available"
        assert lld_pseudo_graph is not None, "LLD Pseudocode graph should be available"


class TestLLDAPIWorkflow:
    """Tests for LLD API Specifications workflow"""

    def test_lld_api_basic_generation(self):
        """Test basic API specifications generation"""
        state = {
            "user_message": "Create API specifications for user management service",
            "content_id": None,
            "storage_paths": None
        }

        result = lld_api_graph.invoke(state)

        assert "response" in result
        assert isinstance(result["response"], dict)
        assert "title" in result["response"]
        assert "api_overview" in result["response"]
        assert "endpoints" in result["response"]
        assert "authentication" in result["response"]

    def test_lld_api_complete_workflow(self):
        """Test complete API specs generation with all fields"""
        state = {
            "user_message": "Generate comprehensive API documentation for e-commerce REST API with authentication, product catalog, shopping cart, and order management",
            "content_id": None,
            "storage_paths": []
        }

        result = lld_api_graph.invoke(state)

        response = result["response"]
        assert response["title"], "Should have title"
        assert response["api_overview"], "Should have API overview"
        assert response["authentication"], "Should have authentication details"
        assert response["endpoints"], "Should specify endpoints"
        assert response["data_models"], "Should include data models"
        assert response["error_handling"], "Should describe error handling"
        assert response["rate_limiting"], "Should specify rate limiting"
        assert response["versioning"], "Should describe versioning"
        assert response["detail"], "Should have detailed documentation"

    def test_lld_api_with_context(self):
        """Test API specs generation with extracted content"""
        state = {
            "user_message": "Create API documentation",
            "content_id": None,
            "storage_paths": None,
            "extracted_text": "Requirements: REST API for booking system with authentication, availability check, and reservation endpoints",
            "chat_context": None
        }

        result = lld_api_graph.invoke(state)
        assert "response" in result
        assert result["response"]["endpoints"], "Should generate endpoints"

    def test_lld_api_microservices(self):
        """Test API specs for microservices architecture"""
        state = {
            "user_message": "Generate API specifications for payment microservice with webhook support",
            "content_id": None,
            "storage_paths": None
        }

        result = lld_api_graph.invoke(state)
        response = result["response"]
        assert "title" in response
        assert "api_overview" in response


class TestLLDDBWorkflow:
    """Tests for LLD Database Schema workflow"""

    def test_lld_db_basic_generation(self):
        """Test basic database schema generation"""
        state = {
            "user_message": "Create database schema for blog application",
            "content_id": None,
            "storage_paths": None
        }

        result = lld_db_graph.invoke(state)

        assert "response" in result
        assert isinstance(result["response"], dict)
        assert "type" in result["response"]
        assert "detail" in result["response"]

    def test_lld_db_complete_workflow(self):
        """Test complete database schema generation with ERD"""
        state = {
            "user_message": "Generate database schema for e-commerce platform with users, products, orders, payments, and reviews",
            "content_id": None,
            "storage_paths": []
        }

        result = lld_db_graph.invoke(state)

        response = result["response"]
        assert response["type"], "Should specify diagram type"
        assert response["detail"], "Should have detailed ERD in Mermaid format"
        assert len(response["detail"]) > 100, "Should generate substantial schema"

    def test_lld_db_with_relationships(self):
        """Test database schema with complex relationships"""
        state = {
            "user_message": "Create database schema for social media platform with users, posts, comments, likes, follows, and messages",
            "content_id": None,
            "storage_paths": None
        }

        result = lld_db_graph.invoke(state)
        response = result["response"]
        assert "detail" in response
        assert response["type"] in ["erDiagram", "database-schema", "entity-relationship"]

    def test_lld_db_with_context(self):
        """Test database schema with requirements context"""
        state = {
            "user_message": "Generate database design",
            "content_id": None,
            "storage_paths": None,
            "extracted_text": "System requirements: User authentication, profile management, activity logging, and notifications",
            "chat_context": None
        }

        result = lld_db_graph.invoke(state)
        assert "response" in result
        assert "detail" in result["response"]

    def test_lld_db_normalized_design(self):
        """Test database schema for normalized design"""
        state = {
            "user_message": "Create normalized database schema for library management system with books, authors, members, loans, and reservations",
            "content_id": None,
            "storage_paths": []
        }

        result = lld_db_graph.invoke(state)
        response = result["response"]
        assert "type" in response
        assert "detail" in response


class TestLLDArchWorkflow:
    """Tests for LLD Architecture Diagram workflow"""

    def test_lld_arch_basic_generation(self):
        """Test basic architecture diagram generation"""
        state = {
            "user_message": "Create low-level architecture diagram for authentication module",
            "content_id": None,
            "storage_paths": None
        }

        result = lld_arch_graph.invoke(state)

        assert "response" in result
        assert isinstance(result["response"], dict)
        assert "type" in result["response"]
        assert "detail" in result["response"]

    def test_lld_arch_complete_workflow(self):
        """Test complete architecture diagram generation"""
        state = {
            "user_message": "Generate detailed low-level architecture for payment processing module with components, classes, and interactions",
            "content_id": None,
            "storage_paths": []
        }

        result = lld_arch_graph.invoke(state)

        response = result["response"]
        assert response["type"], "Should specify diagram type"
        assert response["detail"], "Should have detailed diagram in Mermaid format"
        assert len(response["detail"]) > 50, "Should generate meaningful architecture"

    def test_lld_arch_component_diagram(self):
        """Test architecture with component breakdown"""
        state = {
            "user_message": "Create low-level component diagram for notification service with queuing, processing, and delivery components",
            "content_id": None,
            "storage_paths": None
        }

        result = lld_arch_graph.invoke(state)
        response = result["response"]
        assert "type" in response
        assert "detail" in response

    def test_lld_arch_class_structure(self):
        """Test architecture showing class structure"""
        state = {
            "user_message": "Generate class-level architecture diagram for shopping cart module",
            "content_id": None,
            "storage_paths": None
        }

        result = lld_arch_graph.invoke(state)
        assert "response" in result
        assert result["response"]["detail"]

    def test_lld_arch_with_extracted_text(self):
        """Test architecture diagram with requirements"""
        state = {
            "user_message": "Create architecture diagram",
            "content_id": None,
            "storage_paths": None,
            "extracted_text": "Module: Order Processing. Components: OrderValidator, PaymentGateway, InventoryManager, NotificationService",
            "chat_context": None
        }

        result = lld_arch_graph.invoke(state)
        assert "response" in result
        assert "detail" in result["response"]


class TestLLDPseudoWorkflow:
    """Tests for LLD Pseudocode workflow"""

    def test_lld_pseudo_basic_generation(self):
        """Test basic pseudocode generation"""
        state = {
            "user_message": "Create pseudocode for binary search algorithm",
            "content_id": None,
            "storage_paths": None
        }

        result = lld_pseudo_graph.invoke(state)

        assert "response" in result
        assert isinstance(result["response"], dict)
        assert "title" in result["response"]
        assert "pseudocode" in result["response"]

    def test_lld_pseudo_complete_workflow(self):
        """Test complete pseudocode generation with all fields"""
        state = {
            "user_message": "Generate complete pseudocode for sorting algorithm with complexity analysis and edge cases",
            "content_id": None,
            "storage_paths": []
        }

        result = lld_pseudo_graph.invoke(state)

        response = result["response"]
        assert response["title"], "Should have title"
        assert response["algorithm_overview"], "Should have algorithm overview"
        assert response["input_output"], "Should specify input/output"
        assert response["pseudocode"], "Should have pseudocode"
        assert response["complexity_analysis"], "Should include complexity analysis"
        assert response["edge_cases"], "Should describe edge cases"
        assert response["implementation_notes"], "Should have implementation notes"
        assert response["detail"], "Should have detailed documentation"

    def test_lld_pseudo_algorithm_types(self):
        """Test pseudocode for different algorithm types"""
        algorithms = [
            "depth-first search for graph traversal",
            "dynamic programming solution for knapsack problem",
            "merge sort implementation",
            "hash table with collision handling"
        ]

        for algorithm in algorithms:
            state = {
                "user_message": f"Create pseudocode for {algorithm}",
                "content_id": None,
                "storage_paths": None
            }

            result = lld_pseudo_graph.invoke(state)
            assert "response" in result, f"Should generate response for {algorithm}"
            assert "pseudocode" in result["response"], f"Should have pseudocode for {algorithm}"

    def test_lld_pseudo_with_complexity(self):
        """Test pseudocode with complexity analysis"""
        state = {
            "user_message": "Generate pseudocode for quicksort with time and space complexity analysis",
            "content_id": None,
            "storage_paths": None
        }

        result = lld_pseudo_graph.invoke(state)
        response = result["response"]
        assert "complexity_analysis" in response
        assert len(response["complexity_analysis"]) > 0

    def test_lld_pseudo_business_logic(self):
        """Test pseudocode for business logic"""
        state = {
            "user_message": "Create pseudocode for order validation and payment processing workflow",
            "content_id": None,
            "storage_paths": []
        }

        result = lld_pseudo_graph.invoke(state)
        response = result["response"]
        assert "title" in response
        assert "pseudocode" in response
        assert "edge_cases" in response

    def test_lld_pseudo_with_context(self):
        """Test pseudocode generation with context"""
        state = {
            "user_message": "Generate pseudocode for the algorithm",
            "content_id": None,
            "storage_paths": None,
            "extracted_text": "Algorithm: Find shortest path in weighted graph using Dijkstra's algorithm",
            "chat_context": None
        }

        result = lld_pseudo_graph.invoke(state)
        assert "response" in result
        assert "pseudocode" in result["response"]


class TestLLDCrossWorkflow:
    """Cross-workflow integration tests for LLD phase"""

    def test_lld_response_consistency(self):
        """Test that all LLD workflows return consistent response structures"""
        test_message = "Create design for user authentication system"

        # Test API workflow
        api_result = lld_api_graph.invoke({"user_message": test_message})
        assert "response" in api_result
        assert isinstance(api_result["response"], dict)

        # Test DB workflow
        db_result = lld_db_graph.invoke({"user_message": test_message})
        assert "response" in db_result
        assert isinstance(db_result["response"], dict)

        # Test Arch workflow
        arch_result = lld_arch_graph.invoke({"user_message": test_message})
        assert "response" in arch_result
        assert isinstance(arch_result["response"], dict)

        # Test Pseudo workflow
        pseudo_result = lld_pseudo_graph.invoke({"user_message": test_message})
        assert "response" in pseudo_result
        assert isinstance(pseudo_result["response"], dict)

    def test_lld_handles_content_id(self):
        """Test that all LLD workflows handle content_id parameter"""
        content_id = "test-conversation-id"
        
        for graph, name in [
            (lld_api_graph, "API"),
            (lld_db_graph, "DB"),
            (lld_arch_graph, "Arch"),
            (lld_pseudo_graph, "Pseudo")
        ]:
            state = {
                "user_message": f"Create {name} design",
                "content_id": content_id,
                "storage_paths": None
            }
            result = graph.invoke(state)
            assert "response" in result, f"{name} workflow should handle content_id"

    def test_lld_handles_storage_paths(self):
        """Test that all LLD workflows handle storage_paths parameter"""
        storage_paths = ["test-path-1.pdf", "test-path-2.pdf"]
        
        for graph, name in [
            (lld_api_graph, "API"),
            (lld_db_graph, "DB"),
            (lld_arch_graph, "Arch"),
            (lld_pseudo_graph, "Pseudo")
        ]:
            state = {
                "user_message": f"Generate {name} documentation",
                "content_id": None,
                "storage_paths": storage_paths
            }
            result = graph.invoke(state)
            assert "response" in result, f"{name} workflow should handle storage_paths"

    def test_lld_state_preservation(self):
        """Test that workflows preserve state fields"""
        state = {
            "user_message": "Create system design",
            "content_id": "test-123",
            "storage_paths": ["path1.pdf"],
            "extracted_text": "Context information",
            "chat_context": "Previous conversation"
        }

        result = lld_api_graph.invoke(state)
        assert "response" in result
        # User message should be preserved
        assert result.get("user_message") == "Create system design"
