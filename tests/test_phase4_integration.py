import pytest
from workflows.hld_arch_workflow import hld_arch_graph
from workflows.hld_cloud_workflow import hld_cloud_graph
from workflows.hld_tech_workflow import hld_tech_graph


class TestPhase4Integration:
    """Comprehensive integration tests for Phase 4 High-Level Design workflows."""
    
    def test_all_phase4_workflows_available(self):
        """Verify all Phase 4 workflow graphs are importable and callable."""
        # All graphs should be available
        assert hld_arch_graph is not None
        assert hld_cloud_graph is not None
        assert hld_tech_graph is not None
        
        # All should have invoke method
        assert hasattr(hld_arch_graph, 'invoke')
        assert hasattr(hld_cloud_graph, 'invoke')
        assert hasattr(hld_tech_graph, 'invoke')
    
    def test_hld_arch_basic_execution(self):
        """Test basic execution of architecture diagram workflow."""
        state = {
            "user_message": "Generate system architecture",
            "content_id": None,
            "storage_paths": []
        }
        
        result = hld_arch_graph.invoke(state)
        assert "response" in result
        assert result["response"]["type"] == "hld-arch"
        assert len(result["response"]["detail"]) > 0
    
    def test_hld_cloud_basic_execution(self):
        """Test basic execution of cloud infrastructure workflow."""
        state = {
            "user_message": "Generate cloud infrastructure",
            "content_id": None,
            "storage_paths": []
        }
        
        result = hld_cloud_graph.invoke(state)
        assert "response" in result
        response = result["response"]
        
        # Verify all 9 fields
        assert "title" in response
        assert "cloud_provider" in response
        assert "infrastructure_components" in response
        assert "deployment_architecture" in response
        assert "scaling_strategy" in response
        assert "security_measures" in response
        assert "monitoring_logging" in response
        assert "cost_estimation" in response
        assert "detail" in response
    
    def test_hld_tech_basic_execution(self):
        """Test basic execution of technology stack workflow."""
        state = {
            "user_message": "Generate technology stack",
            "content_id": None,
            "storage_paths": []
        }
        
        result = hld_tech_graph.invoke(state)
        assert "response" in result
        response = result["response"]
        
        # Verify all 9 fields
        assert "title" in response
        assert "frontend_technologies" in response
        assert "backend_technologies" in response
        assert "database_technologies" in response
        assert "infrastructure_technologies" in response
        assert "integration_technologies" in response
        assert "selection_rationale" in response
        assert "risk_mitigation" in response
        assert "detail" in response
    
    def test_phase4_complete_project_workflow(self):
        """Test complete Phase 4 workflow for a project."""
        project_context = "e-commerce platform with microservices"
        
        # 1. Generate architecture diagram
        arch_state = {
            "user_message": f"Create system architecture for {project_context}",
            "content_id": "ecommerce-001",
            "storage_paths": []
        }
        arch_result = hld_arch_graph.invoke(arch_state)
        assert arch_result["response"]["type"] == "hld-arch"
        arch_diagram = arch_result["response"]["detail"]
        
        # 2. Generate cloud infrastructure
        cloud_state = {
            "user_message": f"Design cloud infrastructure for {project_context}",
            "content_id": "ecommerce-001",
            "storage_paths": []
        }
        cloud_result = hld_cloud_graph.invoke(cloud_state)
        assert "cloud_provider" in cloud_result["response"]
        
        # 3. Generate technology stack
        tech_state = {
            "user_message": f"Select technology stack for {project_context}",
            "content_id": "ecommerce-001",
            "storage_paths": []
        }
        tech_result = hld_tech_graph.invoke(tech_state)
        assert "frontend_technologies" in tech_result["response"]
        assert "backend_technologies" in tech_result["response"]
        
        # All should generate non-empty content
        assert len(arch_diagram) > 0
        assert len(cloud_result["response"]["detail"]) > 0
        assert len(tech_result["response"]["detail"]) > 0
    
    def test_phase4_with_content_id_consistency(self):
        """Test that content_id is properly handled across Phase 4 workflows."""
        content_id = "test-project-789"
        message = "Generate design for banking system"
        
        # Test architecture
        result1 = hld_arch_graph.invoke({
            "user_message": message,
            "content_id": content_id,
            "storage_paths": []
        })
        assert "response" in result1
        
        # Test cloud
        result2 = hld_cloud_graph.invoke({
            "user_message": message,
            "content_id": content_id,
            "storage_paths": []
        })
        assert "response" in result2
        
        # Test tech
        result3 = hld_tech_graph.invoke({
            "user_message": message,
            "content_id": content_id,
            "storage_paths": []
        })
        assert "response" in result3
    
    def test_phase4_with_storage_paths(self):
        """Test Phase 4 workflows with storage paths."""
        storage_paths = [
            "/path/to/requirements.json",
            "/path/to/scope.md",
            "/path/to/business_case.json"
        ]
        
        # Architecture with paths
        arch_result = hld_arch_graph.invoke({
            "user_message": "Create architecture",
            "content_id": "project-001",
            "storage_paths": storage_paths
        })
        assert "response" in arch_result
        
        # Cloud with paths
        cloud_result = hld_cloud_graph.invoke({
            "user_message": "Design cloud infrastructure",
            "content_id": "project-001",
            "storage_paths": storage_paths
        })
        assert "response" in cloud_result
        
        # Tech with paths
        tech_result = hld_tech_graph.invoke({
            "user_message": "Select technologies",
            "content_id": "project-001",
            "storage_paths": storage_paths
        })
        assert "response" in tech_result
    
    def test_phase4_empty_content_id(self):
        """Test Phase 4 workflows handle empty content_id gracefully."""
        # Test with None
        result1 = hld_arch_graph.invoke({
            "user_message": "Generate architecture",
            "content_id": None,
            "storage_paths": []
        })
        assert "response" in result1
        
        # Test with empty string (should be treated as None)
        result2 = hld_cloud_graph.invoke({
            "user_message": "Generate cloud setup",
            "content_id": "",
            "storage_paths": []
        })
        assert "response" in result2
    
    def test_phase4_architecture_diagram_format(self):
        """Verify architecture diagram output is valid Mermaid syntax."""
        result = hld_arch_graph.invoke({
            "user_message": "Create microservices architecture with API gateway, services, and databases",
            "content_id": None,
            "storage_paths": []
        })
        
        diagram = result["response"]["detail"]
        
        # Should contain Mermaid syntax
        assert isinstance(diagram, str)
        assert len(diagram) > 0
        
        # Should have graph declaration or flowchart
        diagram_lower = diagram.lower()
        assert any(keyword in diagram_lower for keyword in [
            "graph", "flowchart", "subgraph"
        ])
        
        # Should have connections
        assert "-->" in diagram or "---" in diagram or "==>" in diagram
    
    def test_phase4_cloud_document_completeness(self):
        """Verify cloud infrastructure document has all required sections."""
        result = hld_cloud_graph.invoke({
            "user_message": "Design AWS cloud infrastructure for scalable web application",
            "content_id": None,
            "storage_paths": []
        })
        
        response = result["response"]
        
        # All fields should have content
        assert len(response["title"]) > 10
        assert len(response["cloud_provider"]) > 0
        assert len(response["infrastructure_components"]) > 50
        assert len(response["deployment_architecture"]) > 50
        assert len(response["scaling_strategy"]) > 30
        assert len(response["security_measures"]) > 30
        assert len(response["monitoring_logging"]) > 30
        assert len(response["cost_estimation"]) > 20
        assert len(response["detail"]) > 100
    
    def test_phase4_tech_stack_completeness(self):
        """Verify technology stack document has all required sections."""
        result = hld_tech_graph.invoke({
            "user_message": "Select modern tech stack for enterprise application",
            "content_id": None,
            "storage_paths": []
        })
        
        response = result["response"]
        
        # All fields should have meaningful content
        assert len(response["title"]) > 10
        assert len(response["frontend_technologies"]) > 30
        assert len(response["backend_technologies"]) > 30
        assert len(response["database_technologies"]) > 20
        assert len(response["infrastructure_technologies"]) > 20
        assert len(response["integration_technologies"]) > 20
        assert len(response["selection_rationale"]) > 50
        assert len(response["risk_mitigation"]) > 30
        assert len(response["detail"]) > 100
    
    def test_phase4_different_project_types(self):
        """Test Phase 4 workflows with different project types."""
        project_types = [
            "mobile application",
            "IoT system",
            "data analytics platform",
            "real-time streaming service"
        ]
        
        for project_type in project_types:
            # Test architecture
            arch_result = hld_arch_graph.invoke({
                "user_message": f"Create architecture for {project_type}",
                "content_id": None,
                "storage_paths": []
            })
            assert arch_result["response"]["type"] == "hld-arch"
            
            # Test cloud
            cloud_result = hld_cloud_graph.invoke({
                "user_message": f"Design cloud for {project_type}",
                "content_id": None,
                "storage_paths": []
            })
            assert "cloud_provider" in cloud_result["response"]
            
            # Test tech
            tech_result = hld_tech_graph.invoke({
                "user_message": f"Select tech stack for {project_type}",
                "content_id": None,
                "storage_paths": []
            })
            assert "frontend_technologies" in tech_result["response"]
