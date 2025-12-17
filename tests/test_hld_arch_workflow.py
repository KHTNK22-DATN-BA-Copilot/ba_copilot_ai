import pytest
from workflows.hld_arch_workflow import hld_arch_graph


def test_hld_arch_workflow_basic():
    """Test basic HLD architecture diagram generation with minimal input."""
    state = {
        "user_message": "Generate a system architecture diagram for an e-commerce platform",
        "content_id": None,
        "storage_paths": []
    }
    
    result = hld_arch_graph.invoke(state)
    
    # Verify result structure
    assert "response" in result
    response = result["response"]
    
    # Verify response has required fields
    assert "type" in response
    assert "detail" in response
    
    # Verify it's an architecture diagram type
    assert response["type"] == "hld-arch"
    
    # Verify detail contains Mermaid diagram syntax
    detail = response["detail"]
    assert isinstance(detail, str)
    assert len(detail) > 0
    # Should contain Mermaid graph syntax indicators
    assert any(keyword in detail.lower() for keyword in ["graph", "flowchart", "-->", "subgraph"])


def test_hld_arch_workflow_with_context():
    """Test HLD architecture diagram generation with content context."""
    state = {
        "user_message": "Create a microservices architecture diagram showing API Gateway, services, and database layers",
        "content_id": "test-content-123",
        "storage_paths": []
    }
    
    result = hld_arch_graph.invoke(state)
    
    # Verify result structure
    assert "response" in result
    response = result["response"]
    
    # Verify response structure
    assert response["type"] == "hld-arch"
    assert len(response["detail"]) > 0
    
    # Verify Mermaid syntax
    detail = response["detail"]
    assert "graph" in detail.lower() or "flowchart" in detail.lower()


def test_hld_arch_workflow_complex_system():
    """Test architecture diagram for a complex distributed system."""
    state = {
        "user_message": "Design a high-level architecture for a video streaming platform with CDN, authentication, content delivery, and analytics",
        "content_id": None,
        "storage_paths": []
    }
    
    result = hld_arch_graph.invoke(state)
    
    # Verify result structure
    assert "response" in result
    response = result["response"]
    
    # Should be a diagram
    assert response["type"] == "hld-arch"
    
    # Should contain meaningful Mermaid diagram
    detail = response["detail"]
    assert isinstance(detail, str)
    assert len(detail) > 100  # Complex system should have substantial diagram
    
    # Should contain Mermaid syntax elements
    assert "-->" in detail or "---" in detail


def test_hld_arch_workflow_with_storage_paths():
    """Test architecture diagram with multiple storage paths."""
    state = {
        "user_message": "Generate architecture for a banking application",
        "content_id": "banking-001",
        "storage_paths": ["/path/to/requirements.txt", "/path/to/scope.json"]
    }
    
    result = hld_arch_graph.invoke(state)
    
    # Verify result
    assert "response" in result
    response = result["response"]
    
    assert response["type"] == "hld-arch"
    assert len(response["detail"]) > 0


def test_hld_arch_workflow_specific_patterns():
    """Test architecture diagram with specific architectural patterns."""
    state = {
        "user_message": "Create architecture using Event-Driven pattern with message queue, event bus, and event handlers",
        "content_id": None,
        "storage_paths": []
    }
    
    result = hld_arch_graph.invoke(state)
    
    # Verify response
    response = result["response"]
    assert response["type"] == "hld-arch"
    
    # Should generate valid Mermaid syntax
    detail = response["detail"]
    assert isinstance(detail, str)
    assert len(detail) > 50


def test_hld_arch_workflow_cloud_native():
    """Test cloud-native architecture diagram."""
    state = {
        "user_message": "Design a cloud-native architecture with containers, orchestration, service mesh, and monitoring",
        "content_id": "cloud-native-arch",
        "storage_paths": []
    }
    
    result = hld_arch_graph.invoke(state)
    
    # Verify diagram generated
    response = result["response"]
    assert response["type"] == "hld-arch"
    assert len(response["detail"]) > 0
    
    # Should be valid Mermaid
    detail = response["detail"]
    assert any(keyword in detail.lower() for keyword in ["graph", "flowchart", "subgraph"])


def test_hld_arch_workflow_layered_architecture():
    """Test layered architecture diagram."""
    state = {
        "user_message": "Generate a 3-tier architecture showing presentation, business logic, and data access layers",
        "content_id": None,
        "storage_paths": []
    }
    
    result = hld_arch_graph.invoke(state)
    
    # Verify structure
    response = result["response"]
    assert response["type"] == "hld-arch"
    assert isinstance(response["detail"], str)
    assert len(response["detail"]) > 0
